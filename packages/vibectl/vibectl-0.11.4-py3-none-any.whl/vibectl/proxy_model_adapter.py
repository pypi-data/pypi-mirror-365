"""
Proxy model adapter for communicating with vibectl LLM proxy server.

This module provides a ModelAdapter implementation that forwards requests
to a remote vibectl LLM proxy server via gRPC, enabling transparent
delegation of LLM calls to a centralized service.
"""

import asyncio
import json
import os
import time
import uuid
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import grpc
from pydantic import BaseModel

from vibectl import __version__
from vibectl.version_compat import check_version_compatibility

from .config import Config
from .logutil import logger
from .model_adapter import ModelAdapter, StreamingMetricsCollector
from .proto import llm_proxy_pb2, llm_proxy_pb2_grpc
from .security import AuditLogger, DetectedSecret, RequestSanitizer, SecurityConfig
from .types import LLMMetrics, SystemFragments, UserFragments


class ProxyModelWrapper:
    """Wrapper class to represent a remote model accessible via proxy."""

    def __init__(self, model_name: str, adapter: "ProxyModelAdapter"):
        self.model_name = model_name
        self.model_id = model_name  # For compatibility with existing code
        self.adapter = adapter

    def __str__(self) -> str:
        return f"ProxyModel({self.model_name})"

    def __repr__(self) -> str:
        return f"ProxyModelWrapper(model_name='{self.model_name}')"


class ProxyStreamingMetricsCollector(StreamingMetricsCollector):
    """Metrics collector for proxy streaming responses."""

    def __init__(self, request_id: str):
        self.request_id = request_id
        self.start_time = time.monotonic()
        self._metrics: LLMMetrics | None = None
        self._completed = False

    def set_final_metrics(self, metrics: LLMMetrics) -> None:
        """Set the final metrics from the proxy response."""
        self._metrics = metrics
        self._completed = True

    async def get_metrics(self) -> LLMMetrics | None:
        """Get the final metrics if available."""
        return self._metrics

    @property
    def completed(self) -> bool:
        """Check if streaming is completed."""
        return self._completed


class ProxyModelAdapter(ModelAdapter):
    """Model adapter that proxies requests to a remote vibectl LLM proxy server."""

    def __init__(
        self,
        config: Config | None = None,
        host: str = "localhost",
        port: int = 50051,
        jwt_token: str | None = None,
        use_tls: bool = True,
    ):
        """Initialize the proxy model adapter.

        Args:
            config: Optional Config instance for client configuration
            host: Proxy server host (default: localhost)
            port: Proxy server port (default: 50051)
            jwt_token: Optional JWT token for authentication (overrides config)
            use_tls: Whether to use TLS encryption (default: True)
        """
        self.config = config or Config()
        self.host = host
        self.port = port
        # JWT token precedence: explicit parameter > profile config resolution
        self.jwt_token: str | None = None
        if jwt_token:
            self.jwt_token = jwt_token
        else:
            # Get JWT token from active proxy profile
            profile_config = self.config.get_effective_proxy_config()
            if profile_config and profile_config.get("jwt_path"):
                try:
                    jwt_path = Path(profile_config["jwt_path"]).expanduser()
                    if jwt_path.exists() and jwt_path.is_file():
                        self.jwt_token = jwt_path.read_text().strip()
                    else:
                        logger.warning(
                            f"JWT file not found: {profile_config['jwt_path']}"
                        )
                        self.jwt_token = None
                except Exception as e:
                    logger.warning(f"Failed to read JWT file: {e}")
                    self.jwt_token = None
            else:
                # Fall back to environment variable
                self.jwt_token = os.environ.get("VIBECTL_JWT_TOKEN")
        self.use_tls = use_tls

        # Initialize sanitizer with security config from profile
        security_config = None
        profile_config = self.config.get_effective_proxy_config()
        if profile_config and profile_config.get("security"):
            # Start with profile-specific security config
            security_dict = profile_config["security"].copy()

            # If warn_sanitization is not set in profile, use global setting
            if "warn_sanitization" not in security_dict:
                global_warn_sanitization = self.config.get(
                    "warnings.warn_sanitization", True
                )
                security_dict["warn_sanitization"] = global_warn_sanitization

            security_config = SecurityConfig.from_dict(security_dict)
        else:
            # No profile security config, use global warnings setting
            global_warn_sanitization = self.config.get(
                "warnings.warn_sanitization", True
            )
            security_config = SecurityConfig(warn_sanitization=global_warn_sanitization)

        self.sanitizer = RequestSanitizer(security_config)

        # Initialize audit logger with security config and active profile name
        profile_name = None
        profile_config = self.config.get_effective_proxy_config()
        if profile_config:
            # Get the active profile name
            active_profile = self.config.get("proxy.active")
            if active_profile:
                profile_name = active_profile

        self.audit_logger = AuditLogger(security_config, proxy_profile=profile_name)

        self.channel: grpc.Channel | None = None
        self.stub: llm_proxy_pb2_grpc.VibectlLLMProxyStub | None = None
        self._model_cache: dict[str, ProxyModelWrapper] = {}
        self._server_info_cache: Any | None = None  # Cache for server info
        self._server_info_cache_time: float = 0.0
        self._server_info_cache_ttl: float = 300.0  # 5 minutes TTL

        logger.debug(
            "ProxyModelAdapter initialized for %s:%d (TLS: %s, Auth: %s)",
            self.host,
            self.port,
            self.use_tls,
            "enabled" if self.jwt_token else "disabled",
        )

    def _get_channel(self) -> grpc.Channel:
        """Get or create the gRPC channel."""
        if self.channel is None:
            target = f"{self.host}:{self.port}"

            if self.use_tls:
                # Get CA bundle path from profile config or environment
                ca_bundle_path = None
                profile_config = self.config.get_effective_proxy_config()
                if profile_config and profile_config.get("ca_bundle_path"):
                    ca_bundle_path = profile_config["ca_bundle_path"]
                else:
                    # Fall back to environment variable
                    ca_bundle_path = os.environ.get("VIBECTL_CA_BUNDLE")

                if ca_bundle_path:
                    # Custom CA bundle TLS
                    try:
                        with open(ca_bundle_path, "rb") as f:
                            ca_cert_data = f.read()
                        credentials = grpc.ssl_channel_credentials(
                            root_certificates=ca_cert_data
                        )
                        logger.debug(
                            "Creating secure channel with custom CA bundle "
                            f"({ca_bundle_path}) to {target} using TLS 1.3+"
                        )
                    except FileNotFoundError as e:
                        raise ValueError(
                            f"CA bundle file not found: {ca_bundle_path}"
                        ) from e
                    except Exception as e:
                        raise ValueError(
                            f"Failed to read CA bundle file {ca_bundle_path}: {e}"
                        ) from e
                else:
                    # Production TLS with system trust store
                    credentials = grpc.ssl_channel_credentials()
                    logger.debug(
                        f"Creating secure channel with system trust store to "
                        f"{target} using TLS 1.3+"
                    )

                # Configure TLS 1.3+ enforcement via gRPC channel options
                channel_options = [
                    # Enforce TLS 1.3+ for enhanced security
                    ("grpc.ssl_min_tls_version", "TLSv1_3"),
                    ("grpc.ssl_max_tls_version", "TLSv1_3"),
                    # Additional security options
                    ("grpc.keepalive_time_ms", 30000),
                    ("grpc.keepalive_timeout_ms", 5000),
                    ("grpc.keepalive_permit_without_calls", True),
                ]

                self.channel = grpc.secure_channel(
                    target, credentials, options=channel_options
                )
            else:
                # Insecure connection (development only)
                logger.debug(f"Creating insecure channel to {target}")
                self.channel = grpc.insecure_channel(target)

            # Create the gRPC stub from the channel
            self.stub = llm_proxy_pb2_grpc.VibectlLLMProxyStub(self.channel)

        return self.channel

    def _get_stub(self) -> llm_proxy_pb2_grpc.VibectlLLMProxyStub:
        """Get or create the gRPC stub."""
        self._get_channel()  # Ensure channel exists
        if self.stub is None:
            raise RuntimeError("Failed to create gRPC stub")
        return self.stub

    def _get_metadata(self) -> list[tuple[str, str]]:
        """Get gRPC metadata including JWT token if available."""
        metadata = []
        if self.jwt_token:
            metadata.append(("authorization", f"Bearer {self.jwt_token}"))
        return metadata

    def _check_version_compatibility(self, server_version: str) -> None:
        """Check for version skew between client and server and warn if needed.

        Args:
            server_version: Version string from the server
        """
        client_version = __version__

        # In 0.x.x versions, any version difference should be reported
        # as it could indicate potential compatibility issues
        if client_version != server_version:
            try:
                # Check if we're in 0.x.x versions (pre-1.0.0)
                client_major = int(client_version.split(".")[0])
                server_major = (
                    int(server_version.split(".")[0]) if "." in server_version else 0
                )

                if client_major == 0 or server_major == 0:
                    # Both are pre-1.0.0, warn about any version skew
                    logger.warning(
                        "Version skew detected: client v%s, server v%s. "
                        "Pre-1.0.0 versions may have compatibility issues. "
                        "Consider updating client and server to the same version.",
                        client_version,
                        server_version,
                    )
                else:
                    # Use semantic versioning compatibility check for 1.0.0+
                    # For now, just warn about differences until we have a formal policy
                    is_compatible, error_msg = check_version_compatibility(
                        client_version, f"=={server_version}"
                    )
                    if not is_compatible:
                        logger.warning(
                            "Version difference detected: client v%s, server v%s. %s",
                            client_version,
                            server_version,
                            error_msg,
                        )
            except (ValueError, IndexError) as e:
                # If we can't parse versions, just log the difference without
                # detailed analysis
                logger.warning(
                    "Version format issue: client v%s, server v%s. Error: %s",
                    client_version,
                    server_version,
                    str(e),
                )

    def _get_server_info(self, force_refresh: bool = False) -> Any:
        """Get server information with alias mappings, using cache when possible.

        Args:
            force_refresh: If True, bypass cache and fetch fresh server info

        Returns:
            GetServerInfoResponse from the server

        Raises:
            grpc.RpcError: If server communication fails
        """
        current_time = time.monotonic()

        # Check if we have valid cached server info
        if (
            not force_refresh
            and self._server_info_cache is not None
            and (current_time - self._server_info_cache_time)
            < self._server_info_cache_ttl
        ):
            logger.debug("Using cached server info")
            return self._server_info_cache

        # Fetch fresh server info
        try:
            stub = self._get_stub()
            request = llm_proxy_pb2.GetServerInfoRequest()  # type: ignore[attr-defined]
            metadata = self._get_metadata()
            response = stub.GetServerInfo(request, timeout=10.0, metadata=metadata)

            # Cache the response
            self._server_info_cache = response
            self._server_info_cache_time = current_time
            logger.debug("Fetched and cached fresh server info")

            # Check version compatibility and warn about skew
            self._check_version_compatibility(response.server_version)

            return response

        except grpc.RpcError as e:
            logger.error("gRPC error fetching server info: %s", e)
            # If we have stale cached data, use it as fallback
            if self._server_info_cache is not None:
                logger.warning(
                    "Using stale cached server info due to communication error"
                )
                return self._server_info_cache
            raise

    def get_model(self, model_name: str) -> Any:
        """Get a proxy model wrapper by name.

        Args:
            model_name: The name of the model to get (can be an alias)

        Returns:
            ProxyModelWrapper: A wrapper representing the remote model

        Raises:
            ValueError: If the model is not available on the proxy server
        """
        # Check cache first
        if model_name in self._model_cache:
            logger.debug("Model '%s' found in cache", model_name)
            return self._model_cache[model_name]

        # Get server info with alias mappings
        try:
            server_info = self._get_server_info()

            # Get available models from server
            available_models = [
                model.model_id for model in server_info.available_models
            ]

            # Try direct match first
            resolved_model_name = model_name
            if model_name not in available_models:
                # Try alias resolution using server-provided mappings
                alias_result = self._resolve_model_alias_from_server(
                    model_name, server_info
                )
                if alias_result is None:
                    raise ValueError(
                        f"Model '{model_name}' not available on proxy server. "
                        f"Available models: {', '.join(available_models)}"
                    )
                resolved_model_name = alias_result

            # Create and cache the wrapper (use original name for caching to
            # support aliases)
            wrapper = ProxyModelWrapper(resolved_model_name, self)
            self._model_cache[model_name] = (
                wrapper  # Cache by requested name for efficiency
            )
            logger.info(
                "Model '%s' resolved to '%s' and cached",
                model_name,
                resolved_model_name,
            )
            return wrapper

        except grpc.RpcError as e:
            logger.error("gRPC error checking model availability: %s", e)
            raise ValueError(f"Failed to connect to proxy server: {e}") from e
        except Exception as e:
            logger.error("Error getting model '%s': %s", model_name, e)
            raise ValueError(f"Failed to get model '{model_name}': {e}") from e

    def _resolve_model_alias_from_server(
        self,
        alias: str,
        server_info: "llm_proxy_pb2.GetServerInfoResponse",  # type: ignore[name-defined]
    ) -> str | None:
        """Resolve a model alias using server-provided alias mappings.

        Args:
            alias: The alias to resolve (e.g., 'claude-4-sonnet')
            server_info: GetServerInfoResponse containing alias mappings

        Returns:
            The resolved model name, or None if no match found
        """
        # Get available models for validation
        available_models = [model.model_id for model in server_info.available_models]

        # First, try the global server alias mappings
        if hasattr(server_info, "model_aliases"):
            server_aliases = dict(server_info.model_aliases)
            if alias in server_aliases:
                mapped_name = server_aliases[alias]
                if mapped_name in available_models:
                    logger.debug(
                        "Resolved alias '%s' to '%s' using server mappings",
                        alias,
                        mapped_name,
                    )
                    return str(mapped_name)  # Explicitly cast to str

        # Second, check per-model aliases from ModelInfo
        for model_info in server_info.available_models:
            if (
                hasattr(model_info, "aliases")
                and model_info.aliases
                and alias in model_info.aliases
            ):
                logger.debug(
                    "Resolved alias '%s' to '%s' using model-specific aliases",
                    alias,
                    model_info.model_id,
                )
                return str(model_info.model_id)  # Explicitly cast to str

        logger.debug("No alias resolution found for '%s'", alias)
        return None

    def _convert_metrics(self, pb_metrics: Any) -> LLMMetrics | None:
        """Convert protobuf metrics to LLMMetrics."""
        if pb_metrics is None:
            return None

        return LLMMetrics(
            token_input=pb_metrics.input_tokens
            if pb_metrics.HasField("input_tokens")
            else 0,
            token_output=pb_metrics.output_tokens
            if pb_metrics.HasField("output_tokens")
            else 0,
            latency_ms=float(pb_metrics.duration_ms),
            total_processing_duration_ms=float(pb_metrics.duration_ms),
            call_count=1,  # Each proxy call represents one LLM call
            cost_usd=pb_metrics.cost_usd if pb_metrics.HasField("cost_usd") else None,
        )

    def _create_execute_request(
        self,
        model: Any,
        system_fragments: SystemFragments,
        user_fragments: UserFragments,
        response_model: type[BaseModel] | None = None,
    ) -> tuple[Any, list["DetectedSecret"]]:  # type: ignore[misc]  # Protobuf type not available at type check time
        """Create an ExecuteRequest protobuf message.

        Returns:
            tuple[ExecuteRequest, list[DetectedSecret]]
        """
        if not isinstance(model, ProxyModelWrapper):
            raise ValueError(f"Expected ProxyModelWrapper, got {type(model)}")

        request = llm_proxy_pb2.ExecuteRequest()  # type: ignore[attr-defined]
        request.request_id = str(uuid.uuid4())
        request.model_name = model.model_name

        # Track all detected secrets across fragments
        all_detected_secrets: list[DetectedSecret] = []

        # Sanitize fragments before adding to request if sanitization is enabled
        if self.sanitizer.enabled:
            # Sanitize system fragments
            sanitized_system_fragments = []
            if system_fragments:
                for fragment in system_fragments:
                    sanitized_fragment, detected_secrets = (
                        self.sanitizer.sanitize_request(fragment)
                    )
                    if detected_secrets:
                        all_detected_secrets.extend(detected_secrets)
                        logger.info(
                            f"Detected {len(detected_secrets)} secrets in system "
                            "fragment"
                        )
                        for secret in detected_secrets:
                            logger.debug(
                                f"Detected secret type: {secret.secret_type} "
                                f"(confidence: {secret.confidence:.2f})"
                            )
                    sanitized_system_fragments.append(sanitized_fragment)
                request.system_fragments.extend(sanitized_system_fragments)

            # Sanitize user fragments
            sanitized_user_fragments = []
            if user_fragments:
                for fragment in user_fragments:
                    sanitized_fragment, detected_secrets = (
                        self.sanitizer.sanitize_request(fragment)
                    )
                    if detected_secrets:
                        all_detected_secrets.extend(detected_secrets)
                        logger.info(
                            f"Detected {len(detected_secrets)} secrets in user fragment"
                        )
                        for secret in detected_secrets:
                            logger.debug(
                                f"Detected secret type: {secret.secret_type} "
                                f"(confidence: {secret.confidence:.2f})"
                            )
                    sanitized_user_fragments.append(sanitized_fragment)
                request.user_fragments.extend(sanitized_user_fragments)
        else:
            # No sanitization - add fragments directly
            if system_fragments:
                request.system_fragments.extend(system_fragments)
            if user_fragments:
                request.user_fragments.extend(user_fragments)

        # Add response model schema if provided
        if response_model is not None:
            try:
                schema = response_model.model_json_schema()
                request.response_model_schema = json.dumps(schema)
            except Exception as e:
                logger.warning("Failed to serialize response model schema: %s", e)

        return request, all_detected_secrets

    async def execute(
        self,
        model: Any,
        system_fragments: SystemFragments,
        user_fragments: UserFragments,
        response_model: type[BaseModel] | None = None,
    ) -> tuple[str, LLMMetrics | None]:
        """Execute a prompt on the proxy server.

        Args:
            model: ProxyModelWrapper representing the remote model
            system_fragments: List of system prompt fragments
            user_fragments: List of user prompt fragments
            response_model: Optional Pydantic model for structured JSON response

        Returns:
            tuple[str, LLMMetrics | None]: Response text and metrics

        Raises:
            ValueError: If execution fails
        """
        try:
            stub = self._get_stub()
            request, detected_secrets = self._create_execute_request(
                model, system_fragments, user_fragments, response_model
            )

            logger.debug(
                "Executing request %s for model %s",
                request.request_id,
                request.model_name,
            )

            # Execute the request with authentication metadata
            metadata = self._get_metadata()
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: stub.Execute(request, timeout=60.0, metadata=metadata)
            )

            # Handle response
            if response.HasField("success"):
                success = response.success
                metrics = self._convert_metrics(success.metrics)
                logger.debug(
                    "Request %s completed successfully, actual model: %s",
                    response.request_id,
                    success.actual_model_used,
                )

                # Log the request/response to audit log
                all_fragments: list[str] = []
                if system_fragments:
                    all_fragments.extend(system_fragments)
                if user_fragments:
                    all_fragments.extend(user_fragments)
                request_content = " ".join(all_fragments)

                self.audit_logger.log_llm_request(
                    request_id=request.request_id,
                    request_content=request_content,
                    response_content=success.response_text,
                    secrets_detected=detected_secrets,
                    model_used=success.actual_model_used,
                )

                return success.response_text, metrics
            elif response.HasField("error"):
                error = response.error
                error_msg = (
                    f"Proxy server error ({error.error_code}): {error.error_message}"
                )
                if error.HasField("error_details"):
                    error_msg += f" - {error.error_details}"
                logger.error("Request %s failed: %s", response.request_id, error_msg)

                # Log the failed request to audit log
                error_fragments: list[str] = []
                if system_fragments:
                    error_fragments.extend(system_fragments)
                if user_fragments:
                    error_fragments.extend(user_fragments)
                request_content = " ".join(error_fragments)

                self.audit_logger.log_llm_request(
                    request_id=request.request_id,
                    request_content=request_content,
                    response_content=f"ERROR: {error_msg}",
                    secrets_detected=detected_secrets,
                    model_used=model.model_name,
                    additional_metadata={"error": True, "error_code": error.error_code},
                )

                raise ValueError(error_msg)
            else:
                raise ValueError("Invalid response from proxy server")

        except grpc.RpcError as e:
            logger.error("gRPC error during execute: %s", e)
            raise ValueError(f"Failed to execute request: {e}") from e
        except Exception as e:
            logger.error("Error during execute: %s", e)
            raise ValueError(f"Proxy execution failed: {e}") from e

    async def execute_and_log_metrics(
        self,
        model: Any,
        system_fragments: SystemFragments,
        user_fragments: UserFragments,
        response_model: type[BaseModel] | None = None,
    ) -> tuple[str, LLMMetrics | None]:
        """Execute a prompt and log metrics.

        This is identical to execute() since metrics logging is handled
        by the proxy server.
        """
        return await self.execute(
            model, system_fragments, user_fragments, response_model
        )

    async def stream_execute(
        self,
        model: Any,
        system_fragments: SystemFragments,
        user_fragments: UserFragments,
        response_model: type[BaseModel] | None = None,
    ) -> AsyncIterator[str]:
        """Execute a prompt with streaming response.

        Args:
            model: ProxyModelWrapper representing the remote model
            system_fragments: List of system prompt fragments
            user_fragments: List of user prompt fragments
            response_model: Optional Pydantic model (ignored for streaming)

        Yields:
            str: Response chunks

        Raises:
            ValueError: If streaming fails
        """
        try:
            stub = self._get_stub()
            request, detected_secrets = self._create_execute_request(
                model, system_fragments, user_fragments, response_model
            )

            logger.debug(
                "Starting stream for request %s, model %s",
                request.request_id,
                request.model_name,
            )

            # Create async wrapper for the streaming call
            def _stream_call() -> Any:
                return stub.StreamExecute(
                    request, timeout=60.0, metadata=self._get_metadata()
                )

            stream = await asyncio.get_event_loop().run_in_executor(None, _stream_call)

            # Process streaming chunks
            async for chunk_pb in self._async_stream_wrapper(stream):
                if chunk_pb.HasField("text_chunk") and chunk_pb.text_chunk:
                    yield chunk_pb.text_chunk
                elif chunk_pb.HasField("error"):
                    error = chunk_pb.error
                    error_msg = (
                        f"Proxy server error ({error.error_code}): "
                        f"{error.error_message}"
                    )
                    if error.HasField("error_details"):
                        error_msg += f" - {error.error_details}"
                    logger.error(
                        "Stream error for request %s: %s",
                        chunk_pb.request_id,
                        error_msg,
                    )
                    raise ValueError(error_msg)
                elif chunk_pb.HasField("complete"):
                    logger.debug(
                        "Stream completed for request %s, actual model: %s",
                        chunk_pb.request_id,
                        chunk_pb.complete.actual_model_used,
                    )
                    break
                # final_metrics are handled by stream_execute_and_log_metrics

        except grpc.RpcError as e:
            logger.error("gRPC error during stream_execute: %s", e)
            raise ValueError(f"Failed to stream request: {e}") from e
        except Exception as e:
            logger.error("Error during stream_execute: %s", e)
            raise ValueError(f"Proxy streaming failed: {e}") from e

    async def stream_execute_and_log_metrics(
        self,
        model: Any,
        system_fragments: SystemFragments,
        user_fragments: UserFragments,
        response_model: type[BaseModel] | None = None,
    ) -> tuple[AsyncIterator[str], StreamingMetricsCollector]:
        """Execute a prompt with streaming response and metrics collection.

        Args:
            model: ProxyModelWrapper representing the remote model
            system_fragments: List of system prompt fragments
            user_fragments: List of user prompt fragments
            response_model: Optional Pydantic model (ignored for streaming)

        Returns:
            tuple containing async iterator for response chunks and metrics collector
        """
        try:
            stub = self._get_stub()
            request, detected_secrets = self._create_execute_request(
                model, system_fragments, user_fragments, response_model
            )

            metrics_collector = ProxyStreamingMetricsCollector(request.request_id)

            logger.debug(
                "Starting stream with metrics for request %s, model %s",
                request.request_id,
                request.model_name,
            )

            # Create the streaming iterator with metrics handling
            async def _streaming_iterator() -> AsyncIterator[str]:
                def _stream_call() -> Any:
                    return stub.StreamExecute(
                        request, timeout=60.0, metadata=self._get_metadata()
                    )

                stream = await asyncio.get_event_loop().run_in_executor(
                    None, _stream_call
                )

                async for chunk_pb in self._async_stream_wrapper(stream):
                    if chunk_pb.HasField("text_chunk") and chunk_pb.text_chunk:
                        yield chunk_pb.text_chunk
                    elif chunk_pb.HasField("final_metrics"):
                        metrics = self._convert_metrics(chunk_pb.final_metrics)
                        if metrics:
                            metrics_collector.set_final_metrics(metrics)
                        # After receiving final metrics, we can break
                        break
                    elif chunk_pb.HasField("error"):
                        error = chunk_pb.error
                        error_msg = (
                            f"Proxy server error ({error.error_code}): "
                            f"{error.error_message}"
                        )
                        if error.HasField("error_details"):
                            error_msg += f" - {error.error_details}"
                        logger.error(
                            "Stream error for request %s: %s",
                            chunk_pb.request_id,
                            error_msg,
                        )
                        raise ValueError(error_msg)
                    elif chunk_pb.HasField("complete"):
                        logger.debug(
                            "Stream completed for request %s, actual model: %s",
                            chunk_pb.request_id,
                            chunk_pb.complete.actual_model_used,
                        )
                        # Don't break here - continue to wait for final_metrics chunk

            return _streaming_iterator(), metrics_collector

        except grpc.RpcError as e:
            logger.error("gRPC error during stream_execute_and_log_metrics: %s", e)
            raise ValueError(f"Failed to stream request with metrics: {e}") from e
        except Exception as e:
            logger.error("Error during stream_execute_and_log_metrics: %s", e)
            raise ValueError(f"Proxy streaming with metrics failed: {e}") from e

    async def _async_stream_wrapper(self, stream: Any) -> AsyncIterator[Any]:
        """Convert gRPC streaming response to async iterator."""
        loop = asyncio.get_event_loop()

        def _get_next() -> Any | None:
            try:
                return next(stream)
            except StopIteration:
                return None

        while True:
            chunk = await loop.run_in_executor(None, _get_next)
            if chunk is None:
                break
            yield chunk

    def validate_model_key(self, model_name: str) -> str | None:
        """Validate model key - delegated to proxy server.

        For proxy connections, key validation is handled server-side.
        This method always returns None as keys are managed by the server.

        Args:
            model_name: The name of the model (unused for proxy)

        Returns:
            None: No client-side key validation needed
        """
        logger.debug(
            "Key validation delegated to proxy server for model: %s", model_name
        )
        return None

    def validate_model_name(self, model_name: str) -> str | None:
        """Validate model name against proxy server.

        Args:
            model_name: The name of the model to validate

        Returns:
            Error message if validation fails, None otherwise
        """
        try:
            # Try to get the model, which will validate it exists on the server
            self.get_model(model_name)
            return None
        except ValueError as e:
            return str(e)
        except Exception as e:
            logger.error(
                "Unexpected error validating model name '%s': %s", model_name, e
            )
            return f"Validation error: {e}"

    def refresh_server_info(self) -> None:
        """Refresh server info cache and clear model cache.

        This method forces a fresh fetch of server information and clears
        the model cache to ensure alias mappings are up to date.
        """
        logger.debug("Refreshing server info cache")
        try:
            self._get_server_info(force_refresh=True)
            # Clear model cache since aliases might have changed
            self._model_cache.clear()
            logger.info("Server info cache refreshed and model cache cleared")
        except Exception as e:
            logger.error("Failed to refresh server info: %s", e)
            raise

    def close(self) -> None:
        """Close the gRPC channel and clean up resources."""
        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
            logger.debug("gRPC channel closed")

        # Clear caches
        self._model_cache.clear()
        self._server_info_cache = None
        self._server_info_cache_time = 0.0

    def __enter__(self) -> "ProxyModelAdapter":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
