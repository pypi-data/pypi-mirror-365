"""
Execution logic for the 'vibectl check' subcommand.
"""

import asyncio
from json import JSONDecodeError

from pydantic import ValidationError

from vibectl.config import Config
from vibectl.console import (
    console_manager,
)
from vibectl.k8s_utils import is_kubectl_command_read_only, run_kubectl
from vibectl.llm_utils import run_llm
from vibectl.logutil import logger
from vibectl.memory import (
    get_memory,
    update_memory,
)
from vibectl.model_adapter import RecoverableApiError
from vibectl.prompts.check import plan_check_fragments
from vibectl.schema import (
    CommandAction,
    DoneAction,
    ErrorAction,
    FeedbackAction,
    LLMPlannerResponse,
    ThoughtAction,
    WaitAction,
)
from vibectl.types import (
    Error,
    Fragment,
    LLMMetricsAccumulator,
    OutputFlags,
    PredicateCheckExitCode,
    Result,
    Success,
    SystemFragments,
    UserFragments,
)


def _format_command_for_display(command_parts: list[str]) -> str:
    """Joins command parts, quoting any part that contains a space."""
    return " ".join(f'"{part}"' if " " in part else part for part in command_parts)


async def _get_check_llm_plan(
    model_name: str,
    plan_system_fragments: SystemFragments,
    plan_user_fragments: UserFragments,
    config: Config,
) -> Result:
    """Calls the LLM to get a command plan for 'check' and validates the response."""

    console_manager.print_processing(
        f"Consulting {model_name} to evaluate predicate..."
    )
    logger.debug(
        f"Final 'check' planning prompt:\n{plan_system_fragments} {plan_user_fragments}"
    )

    # 1) Execute the prompt via the shared run_llm helper which handles adapter
    #    lookup, execution, and optional metrics aggregation.
    try:
        llm_response_text, metrics = await run_llm(
            plan_system_fragments,
            plan_user_fragments,
            model_name=model_name,
            config=config,
            response_model=LLMPlannerResponse,
        )
        logger.info("Raw LLM response text for 'check':\n%s", llm_response_text)
        logger.debug(
            "LLM response text for 'check' (repr): %r, Length: %d",
            llm_response_text,
            len(llm_response_text),
        )
    except RecoverableApiError as api_err:
        logger.warning(
            "Recoverable API error during 'check' planning: %s", api_err, exc_info=True
        )
        console_manager.print_error(f"API Error: {api_err}")
        return Error(str(api_err), exception=api_err, halt_auto_loop=False)
    except Exception as e:
        logger.error(
            "Error during LLM 'check' planning interaction: %s", e, exc_info=True
        )
        console_manager.print_error(f"Error evaluating predicate: {e!s}")
        return Error(str(e), exception=e)

    # 2) Parse the response into the expected schema.
    try:
        response = LLMPlannerResponse.model_validate_json(llm_response_text)
        logger.debug("Parsed LLM response object for 'check': %s", response)
        logger.info("Validated ActionType for 'check': %s", response.action.action_type)
        return Success(data=response, metrics=metrics)

    except (JSONDecodeError, ValidationError) as e:
        logger.warning(
            (
                "Failed to parse LLM response for 'check' as JSON (%s). "
                "Response Text: %s..."
            ),
            type(e).__name__,
            llm_response_text[:500],
        )
        error_msg = f"Failed to parse LLM response for 'check' as expected JSON: {e}"
        return Error(error=error_msg, exception=e)


async def run_check_command(
    predicate: str,
    output_flags: OutputFlags,
) -> Result:
    """
    Implements the 'check <predicate>' subcommand logic.
    """
    logger.info(f"Invoking 'check' subcommand with predicate: {predicate}")

    cfg = Config()
    check_max_iterations = cfg.get_typed("check_max_iterations", 10)
    llm_metrics_accumulator = LLMMetricsAccumulator(output_flags)

    logger.info(f"Evaluating predicate: {predicate}")

    system_fragments, base_user_fragments = plan_check_fragments()

    predicate_fragment = Fragment(f"Predicate: {predicate}")

    iteration = 0

    # TODO: Add other limits here (e.g. time limit, token budget, etc.)
    while iteration < check_max_iterations:
        iteration += 1
        logger.info(f"Check iteration {iteration}/{check_max_iterations}")

        memory_context_str = get_memory(cfg)
        memory_context_fragment = Fragment(f"Memory Context:\n{memory_context_str}")

        user_fragments = UserFragments(
            [
                predicate_fragment,
                memory_context_fragment,
                *base_user_fragments,
            ]
        )

        plan_result = await _get_check_llm_plan(
            output_flags.model_name,
            system_fragments,
            user_fragments,
            cfg,
        )

        if isinstance(plan_result, Error):
            logger.error(f"Error from LLM planning for 'check': {plan_result.error}")
            console_manager.print_error(
                f"Error evaluating predicate: {plan_result.error}"
            )
            final_exit_code = (
                plan_result.original_exit_code
                or PredicateCheckExitCode.CANNOT_DETERMINE.value
            )
            plan_result.original_exit_code = final_exit_code
            return plan_result

        # Accumulate and display metrics from planning
        llm_metrics_accumulator.add_metrics(
            plan_result.metrics, f"LLM Check Planning (Iteration {iteration})"
        )

        if not isinstance(plan_result.data, LLMPlannerResponse):
            logger.error(
                "Unexpected data type in Success object from _get_check_llm_plan: "
                f"{type(plan_result.data)}"
            )
            return Error(
                error="Internal error: Unexpected data type from LLM plan.",
                original_exit_code=PredicateCheckExitCode.CANNOT_DETERMINE.value,
                metrics=llm_metrics_accumulator.get_metrics(),
            )

        llm_planner_response: LLMPlannerResponse = plan_result.data
        action = llm_planner_response.action
        action_type_str = action.action_type.value

        logger.info(
            f"LLM planned action for 'check' (Iter {iteration + 1}): {action_type_str}"
        )

        if isinstance(action, DoneAction):
            exit_code = (
                PredicateCheckExitCode(action.exit_code)
                if action.exit_code is not None
                else PredicateCheckExitCode.CANNOT_DETERMINE
            )
            done_message = action.explanation or "Predicate evaluation complete."
            logger.info(
                f"DoneAction received. Exit Code: {exit_code.value}. "
                f"Message: {done_message}"
            )
            if output_flags.show_vibe:
                console_manager.print_vibe(
                    f"Result: {done_message} (Exit Code: {exit_code.value})"
                )

            # Capture and accumulate memory update metrics
            memory_metrics = await update_memory(
                command_message=f"Checking predicate: {predicate} (Result)",
                command_output=f"Determined: {done_message} (Exit: {exit_code.name})",
                vibe_output="",
                model_name=output_flags.model_name,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                memory_metrics, "LLM Memory Update (Result)"
            )

            final_success_result = Success(
                message=done_message,
                original_exit_code=exit_code.value,
                continue_execution=False,
                metrics=llm_metrics_accumulator.get_metrics(),
            )

            # Display total metrics if enabled
            llm_metrics_accumulator.print_total_if_enabled(
                "Total LLM for Check (Completed)"
            )

            logger.debug(f"run_check_command returning Success: {final_success_result}")

            return final_success_result

        elif isinstance(action, ThoughtAction):
            logger.info(f"LLM Thought: {action.text}")
            if output_flags.show_vibe:
                console_manager.print_vibe(f"AI Thought: {action.text}")

            # Capture and accumulate memory update metrics
            memory_metrics = await update_memory(
                command_message=f"Checking predicate: {predicate} "
                f"(Iter {iteration + 1})",
                command_output=f"Thought: {action.text}",
                vibe_output="",
                model_name=output_flags.model_name,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                memory_metrics, f"LLM Memory Update (Thought, Iteration {iteration})"
            )

            logger.info(
                f"LLM planned action for 'check' (Iter {iteration + 1}): "
                f"{action_type_str} - Thought processed, continuing loop."
            )

        elif isinstance(action, CommandAction):
            logger.debug(f"Processing CommandAction: {action}")
            command_to_execute = action.commands

            command_output_str = ""

            if not command_to_execute or not isinstance(command_to_execute, list):
                logger.warning(
                    f"LLM planned a malformed or empty command: {command_to_execute}. "
                    "Re-planning with error."
                )
                # Capture and accumulate memory update metrics
                memory_metrics = await update_memory(
                    command_message=f"Checking predicate: {predicate} "
                    f"(Iter {iteration + 1}) - Malformed Command",
                    command_output=f"LLM planned: {command_to_execute!s}",
                    vibe_output="System detected a malformed command from LLM.",
                    model_name=output_flags.model_name,
                    config=cfg,
                )
                llm_metrics_accumulator.add_metrics(
                    memory_metrics,
                    f"LLM Memory Update (Malformed Command, Iteration {iteration})",
                )
                continue  # Skip to next iteration to re-plan

            display_command = _format_command_for_display(command_to_execute)

            if not is_kubectl_command_read_only(command_to_execute):
                logger.error(
                    f"CRITICAL: LLM for 'check' planned a non-read-only command: "
                    f"{display_command}. Terminating."
                )
                # Capture and accumulate memory update metrics
                memory_metrics = await update_memory(
                    command_message=f"Checking predicate: {predicate} "
                    f"(Iter {iteration + 1}) - Non-Read-Only Command",
                    command_output=f"LLM planned: {display_command}",
                    vibe_output="System detected a non-read-only command from LLM "
                    "for 'check'.",
                    model_name=output_flags.model_name,
                    config=cfg,
                )
                llm_metrics_accumulator.add_metrics(
                    memory_metrics,
                    f"LLM Memory Update (Non-Read-Only Command, Iteration {iteration})",
                )
                return Error(
                    error="LLM planned a non-read-only command. "
                    "This is not allowed for 'vibectl check'.",
                    original_exit_code=PredicateCheckExitCode.CANNOT_DETERMINE.value,
                    metrics=llm_metrics_accumulator.get_metrics(),
                )

            if output_flags.show_kubectl:
                console_manager.print(f"Executing command: {display_command}")

            exec_allowed_exit_codes = (
                tuple(action.allowed_exit_codes)
                if action.allowed_exit_codes is not None
                else (0,)
            )
            cmd_result = run_kubectl(
                command_to_execute,
                allowed_exit_codes=exec_allowed_exit_codes,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                cmd_result.metrics, f"Command Execution (Iteration {iteration})"
            )

            if isinstance(cmd_result, Error):
                logger.warning(
                    f"kubectl command {display_command} failed: {cmd_result.error}"
                )
                command_output_str = f"Error executing command: {cmd_result.error}"
                if output_flags.show_raw_output and cmd_result.error:
                    console_manager.print(cmd_result.error)
            else:
                command_output_str = (
                    cmd_result.data if cmd_result.data is not None else ""
                )
                logger.info(f"Command output for 'check':\\n{command_output_str}")
                if output_flags.show_raw_output:
                    console_manager.print(command_output_str)

            # Capture and accumulate memory update metrics
            memory_metrics = await update_memory(
                command_message=f"Checking predicate: {predicate} "
                f"(Iter {iteration + 1}) - Ran command: {display_command}",
                command_output=command_output_str,
                vibe_output="",
                model_name=output_flags.model_name,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                memory_metrics, f"LLM Memory Update (Command, Iteration {iteration})"
            )

            logger.info(
                "CommandAction processed for 'check'. Continuing loop for re-planning."
            )

        elif isinstance(action, WaitAction):
            duration = action.duration_seconds
            logger.info(f"WaitAction received. Waiting for {duration}s.")
            if output_flags.show_vibe:
                console_manager.print_vibe(f"AI requests wait for {duration}s.")

            # Capture and accumulate memory update metrics
            memory_metrics = await update_memory(
                command_message=f"Checking predicate: {predicate} "
                f"(Iter {iteration + 1}) - Wait requested",
                command_output=f"AI requested wait for {duration}s.",
                vibe_output="",
                model_name=output_flags.model_name,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                memory_metrics, f"LLM Memory Update (Wait, Iteration {iteration})"
            )

            await asyncio.sleep(duration)

        elif isinstance(action, ErrorAction | FeedbackAction):
            message = getattr(
                action,
                "message",
                getattr(action, "text", "LLM provided intermediate feedback."),
            )
            logger.info(f"{action_type_str} received: {message}. Re-planning.")
            if output_flags.show_vibe:
                console_manager.print_vibe(
                    f"AI ({action_type_str}): {message}. Gathering more information "
                    "or re-planning."
                )

            # Capture and accumulate memory update metrics
            memory_metrics = await update_memory(
                command_message=f"Checking predicate: {predicate} "
                f"(Iter {iteration + 1}) - {action_type_str} received",
                command_output=f"{action_type_str}: {message}",
                vibe_output="",
                model_name=output_flags.model_name,
                config=cfg,
            )
            llm_metrics_accumulator.add_metrics(
                memory_metrics,
                f"LLM Memory Update ({action_type_str}, Iteration {iteration})",
            )

        else:
            logger.warning(
                f"Unhandled action type from LLM for 'check': {action_type_str}"
            )

    # Loop finished due to max_iterations
    logger.warning(f"'check' command reached max iterations ({check_max_iterations}).")

    # Capture and accumulate memory update metrics
    memory_metrics = await update_memory(
        command_message=f"Checking predicate: {predicate} "
        f"(Max Iterations Reached) - {check_max_iterations} iterations",
        command_output="",
        vibe_output="",
        model_name=output_flags.model_name,
        config=cfg,
    )
    llm_metrics_accumulator.add_metrics(
        memory_metrics, "LLM Memory Update (Max Iterations)"
    )

    final_error_result_max_iter = Error(
        error=f"Cannot determine predicate within {check_max_iterations} iterations.",
        original_exit_code=PredicateCheckExitCode.CANNOT_DETERMINE.value,
        metrics=llm_metrics_accumulator.get_metrics(),
    )
    llm_metrics_accumulator.print_total_if_enabled(
        "Total LLM for Check (Max Iterations)"
    )
    return final_error_result_max_iter
