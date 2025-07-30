import asyncio

from vibectl.command_handler import configure_output_flags, handle_command_output
from vibectl.execution.vibe import handle_vibe_request
from vibectl.k8s_utils import run_kubectl
from vibectl.logutil import logger
from vibectl.memory import configure_memory_flags
from vibectl.prompts.scale import scale_plan_prompt, scale_resource_prompt
from vibectl.types import Error, Result, Success


async def run_scale_command(
    resource: str,
    args: tuple[str, ...],
    show_vibe: bool | None,
    freeze_memory: bool,
    unfreeze_memory: bool,
) -> Result:
    """Executes the scale command logic."""

    output_flags = configure_output_flags(
        show_vibe=show_vibe,
    )
    configure_memory_flags(freeze_memory, unfreeze_memory)

    # Handle vibe request first if resource is 'vibe'
    if resource == "vibe":
        if not args or not isinstance(args[0], str):
            return Error("Missing request after 'vibe'")
        request = args[0]

        try:
            vibe_result = await handle_vibe_request(
                request=request,
                command="scale",
                plan_prompt_func=scale_plan_prompt,
                output_flags=output_flags,
                summary_prompt_func=scale_resource_prompt,
                semiauto=False,
                config=None,
            )
            logger.info("Completed 'scale' command for vibe request.")
            return vibe_result
        except Exception as e:
            logger.error(
                "Exception in handle_vibe_request for scale: %s", e, exc_info=True
            )
            return Error(
                error="Exception processing vibe request for scale", exception=e
            )

    # Standard kubectl scale
    try:
        # Build command list
        cmd_list = ["scale", resource, *args]
        logger.info(f"Running kubectl command: {' '.join(cmd_list)}")

        # Run kubectl and get result (capture is always True in run_kubectl now)
        output = await asyncio.to_thread(run_kubectl, cmd_list)

        # Handle errors from kubectl
        if isinstance(output, Error):
            return output

        if output.data:
            try:
                # handle_command_output is synchronous
                _ = await handle_command_output(
                    output=output,
                    command="scale",
                    output_flags=output_flags,
                    summary_prompt_func=scale_resource_prompt,
                )
            except Exception as e:
                logger.error(
                    "Error processing kubectl scale output: %s", e, exc_info=True
                )
                return Error(error="Exception processing scale output", exception=e)
        else:
            logger.info("No output from kubectl scale command.")
            return Success(message="No output from kubectl scale command.")

        logger.info(f"Completed 'scale' command for resource: {resource}")
        return Success(message=f"Successfully processed scale command for {resource}")
    except Exception as e:
        logger.error("Error running kubectl scale: %s", e, exc_info=True)
        return Error(error="Exception running kubectl scale", exception=e)
