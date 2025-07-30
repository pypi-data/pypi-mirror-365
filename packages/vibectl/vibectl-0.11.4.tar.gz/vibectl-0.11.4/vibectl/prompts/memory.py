"""
Prompt templates for memory-related LLM interactions.

This module contains prompts for:
- Memory update operations
- Memory fuzzy update operations
"""

from __future__ import annotations

from typing import Any

from vibectl.config import Config
from vibectl.prompts.context import build_context_fragments
from vibectl.types import Fragment, PromptFragments, SystemFragments, UserFragments

from .shared import (
    FRAGMENT_MEMORY_ASSISTANT,
    fragment_concision,
    fragment_current_time,
    with_custom_prompt_override,
)


def memory_update_prompt(
    command_message: str,
    command_output: str,
    vibe_output: str,
    current_memory: str,
    config: Config | None = None,
) -> PromptFragments:
    """Generate system and user fragments for memory update."""
    cfg = config or Config()
    max_chars = int(cfg.get("memory.max_chars", 500))

    system_fragments: SystemFragments = SystemFragments(
        [
            FRAGMENT_MEMORY_ASSISTANT,
            fragment_concision(max_chars),
            Fragment("Based on the context and interaction, give the updated memory."),
        ]
    )

    # Standard context fragments (memory, custom instructions, timestamp, etc.)
    system_fragments.extend(
        build_context_fragments(
            cfg,
            current_memory=current_memory,
        )
    )

    fragment_interaction = Fragment(f"""Interaction:
Action: {command_message}
Output: {command_output}
Vibe: {vibe_output}
""")

    user_fragments: UserFragments = UserFragments(
        [
            fragment_interaction,
            Fragment("New Memory Summary:"),
        ]
    )
    return PromptFragments((system_fragments, user_fragments))


@with_custom_prompt_override("memory_update")
def memory_fuzzy_update_prompt(
    custom_mapping: Any,
    current_memory: str,
    update_text: str | None = None,
    config: Config | None = None,
) -> PromptFragments:
    """Generate system and user fragments for fuzzy memory update.

    Args:
        custom_mapping: Plugin mapping with custom instructions (may be None)
        current_memory: Current memory content
        update_text: Text to update memory with
        config: Optional Config instance

    Returns:
        PromptFragments: System and user fragments for memory update
    """
    cfg = config or Config()
    max_chars = int(cfg.get("memory.max_chars", 500))

    # Use custom instructions if provided by plugin
    if custom_mapping and custom_mapping.get("description"):
        memory_instruction = Fragment(custom_mapping.get("description"))
    else:
        memory_instruction = Fragment(
            "Based on the user's new information, give the updated memory."
        )

    # Build base system fragments and push down any custom instructions or
    # the default memory_instruction.  This avoids duplicating almost-identical
    # lists across the conditional branches.
    system_fragments = SystemFragments(
        [
            FRAGMENT_MEMORY_ASSISTANT,
            fragment_concision(max_chars),
        ]
    )

    custom_sys_instr = (
        custom_mapping.get("system_instructions") if custom_mapping else None
    )
    system_fragments.append(
        Fragment(custom_sys_instr) if custom_sys_instr else memory_instruction
    )

    # Inject standard context fragments (memory, timestamp, etc.) after any
    # custom system fragments
    system_fragments.extend(
        build_context_fragments(
            cfg,
            current_memory=current_memory,
        )
    )

    # Use custom user template if provided by plugin
    if custom_mapping and custom_mapping.get("user_template"):
        current_time_str = fragment_current_time()
        user_content = custom_mapping.get("user_template").format(
            current_memory=current_memory,
            update_text=update_text or "",
            current_time=str(current_time_str),
        )
        user_fragments = UserFragments([Fragment(user_content)])
    else:
        user_fragments = UserFragments(
            [
                Fragment(f"User Update: {update_text}"),
                Fragment("New Memory Summary:"),
            ]
        )

    return PromptFragments((system_fragments, user_fragments))
