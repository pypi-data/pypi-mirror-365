"""Memory management for vibectl.

This module provides functionality for managing and updating the memory
that is maintained between vibectl commands.
"""

import logging
from typing import cast  # Added List, Tuple

from .config import Config
from .llm_utils import run_llm
from .model_adapter import (
    get_model_adapter,  # noqa: F401, import retained for backward-compat in tests
)
from .prompts.memory import (
    memory_update_prompt,  # Import the fragment-based prompt function
)
from .types import (
    LLMMetrics,
    RecoverableApiError,
)

logger = logging.getLogger(__name__)


def get_memory(config: Config | None = None) -> str:
    """Get current memory content from configuration.

    Args:
        config: Optional Config instance. If not provided, creates a new one.

    Returns:
        str: Current memory content or empty string if not set
    """
    cfg = config or Config()
    return cast("str", cfg.get("memory_content", ""))


def is_memory_enabled(config: Config | None = None) -> bool:
    """Check if memory is enabled.

    Args:
        config: Optional Config instance. If not provided, creates a new one.

    Returns:
        bool: True if memory is enabled, False otherwise
    """
    cfg = config or Config()
    return cast("bool", cfg.get("memory.enabled", True))


def set_memory(memory_text: str, config: Config | None = None) -> None:
    """Set memory content, respecting the maximum length limit.

    Args:
        memory_text: The memory content to set
        config: Optional Config instance. If not provided, creates a new one.
    """
    cfg = config or Config()
    max_chars = cfg.get("memory.max_chars", 500)

    # Truncate if needed
    if memory_text and len(memory_text) > max_chars:
        memory_text = memory_text[:max_chars]

    cfg.set("memory_content", memory_text)
    cfg.save()


def enable_memory(config: Config | None = None) -> None:
    """Enable memory updates.

    Args:
        config: Optional Config instance. If not provided, creates a new one.
    """
    cfg = config or Config()
    cfg.set("memory.enabled", True)
    cfg.save()


def disable_memory(config: Config | None = None) -> None:
    """Disable memory updates.

    Args:
        config: Optional Config instance. If not provided, creates a new one.
    """
    cfg = config or Config()
    cfg.set("memory.enabled", False)
    cfg.save()


def clear_memory(config: Config | None = None) -> None:
    """Clear memory content.

    Args:
        config: Optional Config instance. If not provided, creates a new one.
    """
    cfg = config or Config()
    cfg.set("memory_content", "")
    cfg.save()


async def update_memory(
    command_message: str,
    command_output: str,
    vibe_output: str,
    model_name: str | None = None,
    config: Config | None = None,
) -> LLMMetrics | None:
    """Update memory with the latest interaction using LLM-based summarization."""
    cfg = config or Config()
    if not is_memory_enabled(cfg):
        logger.debug("Memory is disabled, skipping update.")
        return None

    try:
        model_name = model_name or cfg.get("model")

        # Prepare fragments
        current_memory_text = get_memory(cfg)
        system_fragments, user_fragments = memory_update_prompt(
            command_message=command_message,
            command_output=command_output,
            vibe_output=vibe_output,
            current_memory=current_memory_text,
            config=cfg,
        )

        updated_memory_text, metrics = await run_llm(
            system_fragments,
            user_fragments,
            model_name,
            config=cfg,
        )

        if updated_memory_text:
            set_memory(updated_memory_text.strip(), cfg)  # Pass the stripped text
            logger.info("Memory updated successfully.")
            if metrics:
                logger.debug(f"Memory update LLM metrics: {metrics}")
            return metrics  # Return the metrics from the LLM call
        else:
            logger.warning("Memory update LLM call returned empty.")
            return None

    except (RecoverableApiError, ValueError) as e:
        # For now, just ignore errors updating memory to avoid disrupting flow
        logger.warning(f"Ignoring memory update error: {e}")
        return None
    except Exception:
        # Log unexpected errors if logger is available
        logger.exception("Unexpected error updating memory")
        return None  # Ignore unexpected errors too for now


def configure_memory_flags(freeze: bool, unfreeze: bool) -> None:
    """Configure memory behavior based on flags.

    Args:
        freeze: Whether to disable memory updates for this command
        unfreeze: Whether to enable memory updates for this command

    Raises:
        ValueError: If both freeze and unfreeze are specified
    """
    if freeze and unfreeze:
        raise ValueError("Cannot specify both --freeze-memory and --unfreeze-memory")

    cfg = Config()

    if freeze:
        disable_memory(cfg)
    elif unfreeze:
        enable_memory(cfg)


def get_memory_file_path() -> str:
    # This function is not provided in the original file or the code block
    # It's assumed to exist as it's called in the update_memory function
    # It's also not used in the original file or the code block
    # It's left unchanged as it's not clear what it's supposed to do
    return ""  # Placeholder return, actual implementation needed
