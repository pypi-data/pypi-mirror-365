from vibectl.command_handler import (
    configure_output_flags,
    handle_standard_command,
    handle_watch_with_live_display,
)
from vibectl.execution.vibe import handle_vibe_request
from vibectl.logutil import logger
from vibectl.memory import configure_memory_flags
from vibectl.prompts.get import (
    get_plan_prompt,
    get_resource_prompt,
)
from vibectl.types import Error, Result


async def run_get_command(
    resource: str,
    args: tuple,
    show_vibe: bool | None,
    freeze_memory: bool,
    unfreeze_memory: bool,
) -> Result:
    """
    Implements the 'get' subcommand logic, including logging and error handling.
    Returns a Result (Success or Error).
    """
    logger.info(f"Invoking 'get' subcommand with resource: {resource}, args: {args}")
    try:
        output_flags = configure_output_flags(
            show_vibe=show_vibe,
        )
        configure_memory_flags(freeze_memory, unfreeze_memory)

        if resource == "vibe":
            if len(args) < 1:
                msg = (
                    "Missing request after 'vibe' command. "
                    "Please provide a natural language request, e.g.: "
                    'vibectl get vibe "all nginx pods in kube-system"'
                )
                return Error(error=msg)
            request = " ".join(args)
            logger.info(f"Planning how to: {request}")

            result = await handle_vibe_request(
                request=request,
                command="get",
                plan_prompt_func=get_plan_prompt,
                summary_prompt_func=get_resource_prompt,
                output_flags=output_flags,
            )

            # Forward the Result from handle_vibe_request
            if isinstance(result, Error):
                logger.error(f"Error from handle_vibe_request: {result.error}")
                return result

            logger.info("Completed 'get' subcommand for vibe request.")
            return result

        # Check for --watch flag
        watch_flag_present = "--watch" in args or "-w" in args

        if watch_flag_present:
            logger.info("Handling 'get' command with --watch flag using live display.")
            # Await the async handler
            result = await handle_watch_with_live_display(
                command="get",
                resource=resource,
                args=args,
                output_flags=output_flags,
                summary_prompt_func=get_resource_prompt,
            )

        else:
            # Run the sync handler in a thread
            logger.info("Handling standard 'get' command.")
            result = await handle_standard_command(
                command="get",
                resource=resource,
                args=args,
                output_flags=output_flags,
                summary_prompt_func=get_resource_prompt,
            )

        # Forward the Result from the chosen handler
        if isinstance(result, Error):
            logger.error(f"Error from command handler: {result.error}")
            return result

        logger.info(f"Completed 'get' subcommand for resource: {resource}")

        # Return the result directly from the handler
        return result

    except Exception as e:
        logger.error("Error in 'get' subcommand: %s", e, exc_info=True)
        return Error(
            error="Exception in 'get' subcommand",
            exception=e,
        )
