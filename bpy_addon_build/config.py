from __future__ import annotations

import sys
import traceback
from typing import Dict, List, Literal, Optional, TypedDict

from attrs import frozen
from rich.console import Console
from typing_extensions import NotRequired

from .util import EXIT_FAIL, check_string, print_error

ADDON_FOLDER: Literal["addon_folder"] = "addon_folder"
BUILD_NAME: Literal["build_name"] = "build_name"
INSTALL_VERSIONS: Literal["install_versions"] = "install_versions"
BUILD_ACTIONS: Literal["build_actions"] = "build_actions"
SCRIPT: Literal["script"] = "script"
IGNORE_FILTERS: Literal["ignore_filters"] = "ignore_filters"


class BuildActionDict(TypedDict):
    """TypeDict version of BuildAction"""

    script: NotRequired[str]
    ignore_filters: NotRequired[list[str]]


class ConfigDict(TypedDict):
    """TypeDict version of Config"""

    addon_folder: str
    build_name: str
    install_versions: NotRequired[list[float]]
    build_actions: NotRequired[dict[str, Optional[BuildActionDict]]]


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


def build_config(data: ConfigDict) -> Config:
    """Create a config object to represent the config.

    NOTE: This will terminate the program if an error occurs

    args: Args
        Arguments passed to the CLI.

    data: Dict
        Raw data from YAML config.

    Returns:
        - Config if successful
    """

    console = Console()
    parsed_build_acts: dict[str, BuildAction] = {}
    try:
        if ADDON_FOLDER not in data:
            print_error("addon_folder not defined!", console)
            sys.exit(EXIT_FAIL)

        # Disallow '.' as a folder option
        # as it's been found to cause issues
        # during the copy phase.
        #
        # When used, BpyBuild will recursively
        # copy the build folder, as well as .git,
        # leading to a whole load of pain later on.
        #
        # As such, this is simply not allowed.
        elif data[ADDON_FOLDER] == ".":
            print_error("Addon must be in a subfolder!", console)
            sys.exit(EXIT_FAIL)
        elif not check_string(data[ADDON_FOLDER]):
            print_error("addon_folder uses unsupported characters!", console)
            sys.exit(EXIT_FAIL)

        if BUILD_NAME not in data:
            print_error("build_name must be defined!", console)
            sys.exit(EXIT_FAIL)
        elif not check_string(data[BUILD_NAME]):
            print_error("build_name uses unsupported characters!", console)
            sys.exit(EXIT_FAIL)

        if INSTALL_VERSIONS in data:
            for ver in data[INSTALL_VERSIONS]:
                if not isinstance(ver, float):
                    print_error(f"{ver} isn't a valid floating point value", console)
                    sys.exit(EXIT_FAIL)

        if BUILD_ACTIONS in data:
            for act in data[BUILD_ACTIONS]:
                if not check_string(act):
                    print_error(f"{act} uses unsupported characters!", console)
                    sys.exit(EXIT_FAIL)
                action_data = data[BUILD_ACTIONS][act]
                if action_data is not None:
                    # We need to make sure the script name
                    # matches the restrictions we've defined
                    # in check_string. Otherwise, we could
                    # have issues when importing the script
                    # as a module later on.
                    if SCRIPT in action_data and not check_string(
                        action_data[SCRIPT][:-3]
                    ):
                        print_error(
                            f"Script defined for {act} uses unsupported characters in file name!",
                            console,
                        )
                        sys.exit(EXIT_FAIL)

                    # Add the action to parsed_build_acts to
                    # use later in Config construction
                    parsed_build_acts[act] = BuildAction(
                        script=action_data[SCRIPT] if SCRIPT in action_data else None,
                        ignore_filters=action_data[IGNORE_FILTERS]
                        if IGNORE_FILTERS in action_data
                        else None,
                    )
                    continue

                # If an action has nothing defined, what's the
                # point of said action?
                print_error(f"{act} must have something defined!", console)
                sys.exit(EXIT_FAIL)

    except Exception as e:
        console.print(e)
        console.print(traceback.format_exc())
        console.print(data)
        sys.exit(EXIT_FAIL)

    return Config(
        addon_folder=data["addon_folder"],
        build_name=data["build_name"],
        install_versions=data["install_versions"]
        if "install_versions" in data
        else None,
        build_actions=parsed_build_acts if len(parsed_build_acts) else None,
    )
