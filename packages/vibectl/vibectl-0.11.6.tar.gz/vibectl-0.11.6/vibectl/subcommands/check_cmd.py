from vibectl.command_handler import configure_output_flags
from vibectl.execution.check import run_check_command as execute_check_logic
from vibectl.logutil import logger
from vibectl.memory import configure_memory_flags
from vibectl.types import Error, PredicateCheckExitCode, Result


async def run_check_command(
    predicate: str,
    show_vibe: bool | None,
    freeze_memory: bool,
    unfreeze_memory: bool,
) -> Result:
    """
    Implements the 'check' subcommand logic, including logging and error handling.
    Returns a Result (Success or Error).
    """
    logger.info(f"Invoking 'check' subcommand with predicate: \"{predicate}\"")

    if not predicate:
        msg = (
            "Missing predicate for 'check' command. "
            "Please provide a natural language predicate, e.g.: "
            'vibectl check "are there any pods in a CrashLoopBackOff state?"'
        )
        logger.error(msg)
        error_result = Error(error=msg)
        error_result.original_exit_code = PredicateCheckExitCode.POORLY_POSED
        return error_result

    logger.info(f'Evaluating predicate: "{predicate}" using specialized check logic')

    output_flags = configure_output_flags(
        show_vibe=show_vibe,
    )
    configure_memory_flags(freeze_memory, unfreeze_memory)

    result = await execute_check_logic(
        predicate=predicate,
        output_flags=output_flags,
    )

    if isinstance(result, Error):
        logger.error(f"Error from execute_check_logic: {result.error}")
        return result

    logger.info(f"Completed 'check' subcommand for predicate: \"{predicate}\"")

    return result
