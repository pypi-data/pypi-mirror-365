import asyncio

from vibectl.command_handler import (
    configure_output_flags,
    handle_command_output,
)
from vibectl.config import Config
from vibectl.execution.vibe import handle_vibe_request
from vibectl.k8s_utils import run_kubectl
from vibectl.logutil import logger
from vibectl.memory import configure_memory_flags
from vibectl.prompts.diff import diff_output_prompt, diff_plan_prompt
from vibectl.types import (
    Error,
    MetricsDisplayMode,
    Result,
    Success,
)


async def run_diff_command(
    resource: str,
    args: tuple[str, ...],
    show_raw_output: bool | None,
    show_vibe: bool | None,
    show_kubectl: bool | None,
    model: str | None,
    freeze_memory: bool,
    unfreeze_memory: bool,
    show_metrics: MetricsDisplayMode | None,
    show_streaming: bool | None,
) -> Result:
    """
    Implements the 'diff' subcommand logic, including logging and error handling.
    Returns a Result (Success or Error).
    """
    logger.info(f"Invoking 'diff' subcommand with resource: {resource}, args: {args}")
    configure_memory_flags(freeze_memory, unfreeze_memory)

    output_flags = configure_output_flags(
        show_raw_output=show_raw_output,
        show_vibe=show_vibe,
        model=model,
        show_kubectl=show_kubectl,
        show_metrics=show_metrics,
        show_streaming=show_streaming,
    )

    cfg = Config()

    if resource == "vibe":
        if len(args) < 1:
            msg = (
                "Missing request after 'vibe' command. "
                "Please provide a natural language request, e.g.: "
                'vibectl diff vibe "server side new.yaml"'
            )
            return Error(error=msg)
        request = " ".join(args)
        logger.info(f"Planning how to: {request}")

        result = await handle_vibe_request(
            request=request,
            command="diff",
            plan_prompt_func=diff_plan_prompt,
            summary_prompt_func=diff_output_prompt,
            output_flags=output_flags,
        )

        if isinstance(result, Error):
            logger.error(f"Error from handle_vibe_request: {result.error}")
            return result

        logger.info("Completed 'diff' subcommand for vibe request.")
    else:
        cmd = ["diff", resource, *args]

        kubectl_result: Result = await asyncio.to_thread(
            run_kubectl,
            cmd=cmd,
            config=cfg,
            allowed_exit_codes=(0, 1),  # Allow exit code 1 for "differences found"
        )

        if isinstance(kubectl_result, Error):
            logger.error(f"Error running kubectl: {kubectl_result.error}")
            # Propagate the error object
            return kubectl_result

        result = await handle_command_output(
            kubectl_result,
            output_flags=output_flags,
            summary_prompt_func=diff_output_prompt,
            command="diff",
        )

        logger.info("Completed direct 'diff' subcommand execution.")

    # Hack to make sure original exit code is respected
    # TODO: rethink continue_execution flag default value
    if isinstance(result, Success):
        result.continue_execution = False

    return result
