import sys
import traceback

from typing import Dict, List, Optional, TypedDict, Union
from typing_extensions import NotRequired
from attrs import frozen
import cattrs
from cattrs.preconf.pyyaml import make_converter
from rich.console import Console

from .args import Args
from .util import EXIT_FAIL


class BuildActionDict(TypedDict):
    """TypeDict version of BuildAction"""

    script: NotRequired[str]
    ignore_filters: NotRequired[str]


class ConfigDict(TypedDict):
    """TypeDict version of Config"""

    addon_folder: str
    build_name: str
    install_versions: NotRequired[List[float]]
    build_actions: NotRequired[Dict[str, Union[BuildActionDict, None]]]


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@frozen  # type: ignore
class BuildAction:
    """Class that represents a build action

    Attributes
    ----------
    script: Optional[str]
        The Python script associated with the action

    ignore_filters: Optional[List[str]]
        Glob filters to ignore when copying the addon
        folder with this action
    """

    script: Optional[str] = None
    ignore_filters: Optional[List[str]] = None


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@frozen  # type: ignore
class Config:
    """Class to better handle config parsing, especially with more complex arguments

    Attributes
    ----------
    addon_folder: str
        Folder that contains addon code

    build_name: str
        Name of the final build

    versions: Optional[List[float]]
        List of Blender versions to install the final addon to

    actions: Optional[Dict[str, BuildAction]]
        All actions that can occur during the build
    """

    addon_folder: str
    build_name: str
    install_versions: Optional[List[float]] = None
    build_actions: Optional[Dict[str, BuildAction]] = None


def build_config(args: Args, data: ConfigDict) -> Config:
    """Create a config object to represent the config.

    NOTE: This will terminate the program if an exception
    occurs in catters

    args: Args
        Arguments passed to the CLI.

    data: Dict
        Raw data from YAML config.

    Returns:
        - Config if successful
    """

    console = Console()
    try:
        if "addon_folder" not in data:
            console.print("Addon Folder not defined in Config", style="bold red")
            sys.exit(EXIT_FAIL)
        elif data["addon_folder"] == ".":
            console.print("Addon must be in a subfolder!", style="bold red")
            sys.exit(EXIT_FAIL)

        if "build_actions" in data:
            for act in data["build_actions"]:
                if data["build_actions"][act] is not None:
                    continue
                console.print(f"{act} must have something defined!", style="bold red")
                sys.exit(EXIT_FAIL)

        if "install_versions" in data:
            for ver in data["install_versions"]:
                try:
                    _ = float(ver)
                except Exception:
                    console.print(
                        f"{ver} isn't a valid floating point value", style="bold red"
                    )
                    sys.exit(EXIT_FAIL)
    except Exception as e:
        console.print(e)
        console.print(traceback.format_exc())
        console.print(data)
        sys.exit(EXIT_FAIL)

    # Lots of type ignores because cattrs
    # is weird with types, like attrs
    converter = make_converter()
    try:
        return converter.structure(data, Config)  # type: ignore
    except cattrs.errors.ClassValidationError as e:  # type: ignore
        structure_errors: List[KeyError] = []
        for err in e.exceptions[0].exceptions:  # type: ignore
            structure_errors.append(err.exceptions[0])  # type: ignore

        print("Issues in unstructuring the following: ")
        for s in structure_errors:
            print(s)

        if args.debug_mode:
            raise e
        quit(1)
