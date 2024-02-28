from rich.console import Console


def print_warning(msg: str, console: Console) -> None:
    """
    Prints a warning to the console

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="yellow")


def print_error(msg: str, console: Console) -> None:
    """
    Prints an error to the console

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="red")
