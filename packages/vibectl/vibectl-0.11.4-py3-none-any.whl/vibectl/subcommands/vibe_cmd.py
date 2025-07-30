from vibectl.command_handler import (
    configure_output_flags,
)
from vibectl.execution.vibe import (
    handle_vibe_request,
)
from vibectl.logutil import logger
from vibectl.memory import configure_memory_flags
from vibectl.prompts.vibe import plan_vibe_fragments, vibe_autonomous_prompt
from vibectl.types import (
    Error,
    MetricsDisplayMode,
    Result,
    Success,
    determine_execution_mode,
    execution_mode_from_cli,
)


async def run_vibe_command(
    request: str | None,
    show_raw_output: bool | None,
    show_vibe: bool | None,
    show_kubectl: bool | None,
    model: str | None,
    freeze_memory: bool = False,
    unfreeze_memory: bool = False,
    semiauto: bool = False,
    mode_choice: str | None = None,
    exit_on_error: bool = True,
    show_metrics: MetricsDisplayMode | None = None,
    show_streaming: bool | None = None,
) -> Result:
    """
    Implements the 'vibe' subcommand logic, including logging and error handling.
    Returns a Result (Success or Error).

    Args:
        ...
        semiauto: Whether this call is part of a semiauto loop
        exit_on_error: If True (default), errors will terminate the process.
            If False, errors are returned as Error objects for programmatic handling
            (e.g., in tests).
    """
    logger.info(f"Invoking 'vibe' subcommand with request: {request!r}")
    try:
        output_flags = configure_output_flags(
            show_raw_output=show_raw_output,
            show_vibe=show_vibe,
            model=model,
            show_kubectl=show_kubectl,
            show_metrics=show_metrics,
            show_streaming=show_streaming,
        )
        configure_memory_flags(freeze_memory, unfreeze_memory)

        # Handle empty request case
        if not request:
            logger.info("No request provided; using memory context for planning.")
            request = ""
        else:
            logger.info(f"Planning how to: {request}")

        try:
            cli_mode = execution_mode_from_cli(mode_choice)

            exec_mode = (
                cli_mode
                if cli_mode is not None
                else determine_execution_mode(semiauto=semiauto)
            )

            result = await handle_vibe_request(
                request=request,
                command="vibe",
                plan_prompt_func=plan_vibe_fragments,
                summary_prompt_func=vibe_autonomous_prompt,
                output_flags=output_flags,
                execution_mode=exec_mode,
                semiauto=semiauto,
            )

            # Log if it's a normal exit request
            if isinstance(result, Success) and not result.continue_execution:
                logger.info(f"Normal exit requested: {result.message}")

            # Return all results (Success/Error) directly
            return result

        except ValueError as e:
            # Treat ValueErrors from handle_vibe_request (likely LLM planning/parsing
            # issues) as recoverable for auto mode.
            logger.warning(
                f"Recoverable ValueError in handle_vibe_request: {e}", exc_info=True
            )
            if exit_on_error:
                raise  # Still raise if not called from auto/semiauto
            return Error(
                error=f"LLM planning/parsing error: {e!s}",
                exception=e,
                halt_auto_loop=False,  # Mark as recoverable
            )
        except Exception as e:
            # Catch other unexpected errors from handle_vibe_request
            logger.error(
                "Unexpected error in handle_vibe_request: %s", e, exc_info=True
            )
            if exit_on_error:
                raise
            # Use the message from the original exception for the Error object
            # These are likely halting errors by default
            return Error(
                error=f"Unexpected error in handle_vibe_request: {e!s}", exception=e
            )

    except Exception as e:
        logger.error("Error in 'vibe' subcommand: %s", e, exc_info=True)
        if exit_on_error:
            raise
        # Use the message from the original exception for the Error object
        return Error(error=f"Error in vibe command: {e!s}", exception=e)
