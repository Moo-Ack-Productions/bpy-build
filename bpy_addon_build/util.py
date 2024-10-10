import string
import sys

from rich.console import Console

EXIT_FAIL: int = 1

# Define all allowed characters
# for action names and whatnot
#
# This is restricted to the following:
# - ASCII letters (upper and lower)
# - Numeral digits (0-9)
# - Whitespace
# - Hyphens and underscores (to prevent issues with importing modules)
# - Backslash (NOTE: Temporary)
# TODO: Handle backslash in the importing of scripts itself
ALLOWED_CHARS = set(string.ascii_letters + string.digits + string.whitespace + "-_/")


def exit_fail() -> None:
    """Exit the program. This is equal to sys.exit(EXIT_FAIL)"""
    sys.exit(EXIT_FAIL)


def check_string(string: str) -> bool:
    """Check if string has proper input.

    This is for security reasons to reduce
    possible security vectors when running
    BpyBuild, by sanitizing input we have
    no control over.

    This isn't the most performant method but
    for our use case it doesn't matter to much.

    Returns:
        - True if the string has only allowed characters
        - False otherwise
    """
    return set(string) <= ALLOWED_CHARS


def print_warning(msg: str, console: Console) -> None:
    """Prints a warning to the console.

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="yellow")


def print_error(msg: str, console: Console) -> None:
    """Prints an error to the console.

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="red")
