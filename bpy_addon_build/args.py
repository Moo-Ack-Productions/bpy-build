from typing import Self
from pathlib import Path
from attrs import define

HELP_MESSAGE: str = """
Usage:
    bab (-h | --help)
    bab ((-b | --during-build) <action>) [<file>]
    bab [<file>] [((-b | --during-build) <action>)] ((-v | --versions) <versions>...)
    bab [<file>]

Options:
  -h --help     Show this screen.
  -b --during-build      Execute a set of actions in addition to the default action
  -v 
"""

VERSION_MESSAGE: str = "Bpy-Build 0.3.0"

""" 
All arguments defined, converted into their intended 
types to make developer's lives less of a headache.
"""


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@define  # type: ignore
class Args:
    """
    Path to build configuration; by default set to bpy-build.yaml in
    the current directory.

    -c/--config can replace this path, should the user decide to do so
    """

    path: Path = Path("bpy-build.yaml")

    """
    Parses arguments passed in the CLI.

    This is an explicit function to make it clearer what it does.

    Will raise an error on the following conditions:
        - File paths
        -- File does not exist
        -- File is a directory
        -- File is not in the YAML format
        -- -c or --config were passed without a
           path to accompany it

    Returns:
        None
    """

    def parse_args(self: Self) -> None:
        import sys

        for i, arg in enumerate(sys.argv):
            if arg == "-h" or arg == "--help":
                print(HELP_MESSAGE)
            elif arg == "-v" or arg == "--version":
                print(VERSION_MESSAGE)
            if arg == "-c" or arg == "--config":
                next_arg = sys.argv[i + 1] if i < len(sys.argv) else None
                if isinstance(next_arg, str):
                    # People make mistakes and typos, and some
                    # people just want to watch the world burn
                    # by passing invalid files
                    path = Path(next_arg)
                    if not path.exists():
                        raise Exception(f"{str(path)} does not exist!")
                    elif path.is_dir():
                        raise Exception(f"{str(path)} is a directory!")
                    elif path.suffix != ".yaml":
                        raise Exception(f"{str(path)} is not a proper config file!")
                    self.path = path
                else:
                    raise Exception(f"Must pass a path for {arg}!")
