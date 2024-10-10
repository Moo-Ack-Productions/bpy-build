from __future__ import annotations

import traceback
from dataclasses import field
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Dict, List, Literal, Optional, TypedDict

from attrs import frozen
from rich.console import Console
from typing_extensions import NotRequired, Union

from .util import check_string, exit_fail, print_error

# Base settings
ADDON_FOLDER: Literal["addon_folder"] = "addon_folder"
BUILD_NAME: Literal["build_name"] = "build_name"
BUILD_EXTENSION: Literal["build_extension"] = "build_extension"
INSTALL_VERSIONS: Literal["install_versions"] = "install_versions"

# Actions
BUILD_ACTIONS: Literal["build_actions"] = "build_actions"
SCRIPT: Literal["script"] = "script"
IGNORE_FILTERS: Literal["ignore_filters"] = "ignore_filters"
DEPENDS_ON: Literal["depends_on"] = "depends_on"

# Extension Settings
EXTENSION_SETTINGS: Literal["extension_settings"] = "extension_settings"
BUILD_LEGACY: Literal["build_legacy"] = "build_legacy"
REMOVE_BL_INFO: Literal["remove_bl_info"] = "remove_bl_info"

VERSION_JUMPS = {
    "2.83": Decimal(2.9),
    "2.93": Decimal(3.0),
    "3.6": Decimal(4.0),
    "3.60": Decimal(4.0),  # Include version with 0
}


class BuildActionDict(TypedDict):
    """TypeDict version of BuildAction"""

    script: NotRequired[str]
    ignore_filters: NotRequired[list[str]]
    depends_on: NotRequired[list[str]]


class ExtensionSettingsDict(TypedDict):
    """TypeDict verson of ExtensionSettings"""

    build_legacy: NotRequired[bool]
    build_name: NotRequired[str]
    remove_bl_info: NotRequired[bool]


class ConfigDict(TypedDict):
    """TypeDict version of Config"""

    addon_folder: str
    build_name: str
    build_extension: bool
    extension_settings: NotRequired[ExtensionSettingsDict]
    install_versions: NotRequired[list[Union[float, str]]]
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
    depends_on: Optional[list[str]] = None


BUILT_IN_ACTIONS_FOLDER = Path(__file__).parent.joinpath("built_in_actions")
BUILT_IN_ACTS = {
    "extension": BuildAction(str(BUILT_IN_ACTIONS_FOLDER.joinpath("extension.py")))
}


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@frozen  # type: ignore
class ExtensionSettings:
    """Class storing all settings for Blender extensions

    Attributes
    ----------
    build_legacy: bool
        Whether to build a legacy addon or not

    build_name: Optional[str]
        Build name for the built extension. Useful when
        building both a legacy addon and Blender extension

    remove_bl_info: bool
        Whether to remove bl_info or not from an addon

        Note: this is set True if build_legacy is False
    """

    build_legacy: bool
    build_name: Optional[str]
    remove_bl_info: bool


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

    build_extension: bool
        Whether to build a Blender 4.2+ extension

    extension_settings: Optional[ExtensionSettings]
        Settings for building an extension

    versions: Optional[List[float]]
        List of Blender versions to install the final addon to

    actions: Optional[Dict[str, BuildAction]]
        All actions that can occur during the build
    """

    addon_folder: str
    build_name: str
    build_extension: bool = True
    extension_settings: Optional[ExtensionSettings] = None
    install_versions: Optional[List[Decimal]] = None
    build_actions: Optional[Dict[str, BuildAction]] = None
    additional_actions: list[str] = field(default_factory=list)


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
    additional_actions: list[str] = []
    parsed_extension_settings: Optional[ExtensionSettings] = None
    install_versions: list[Decimal] = []

    # Set the precision for Decimal to
    # 3, which corresponds to X.XX
    #
    # This is performed in main, but we
    # do this here as well for sanity purposes
    getcontext().prec = 3

    try:
        if ADDON_FOLDER not in data:
            print_error("addon_folder not defined!", console)
            exit_fail()

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
            exit_fail()
        elif not check_string(data[ADDON_FOLDER]):
            print_error("addon_folder uses unsupported characters!", console)
            exit_fail()

        if BUILD_NAME not in data:
            print_error("build_name must be defined!", console)
            exit_fail()
        elif not check_string(data[BUILD_NAME]):
            print_error("build_name uses unsupported characters!", console)
            exit_fail()

        if BUILD_EXTENSION in data and data[BUILD_EXTENSION]:
            parsed_build_acts["extension"] = BUILT_IN_ACTS["extension"]
            additional_actions.append("extension")
            if EXTENSION_SETTINGS in data:
                extension_settings_data = data[EXTENSION_SETTINGS]
                if (
                    REMOVE_BL_INFO in extension_settings_data
                    and BUILD_LEGACY not in extension_settings_data
                ):
                    print_error(
                        "Cannot set extension_settings::remove_bl_info if legacy builds are not performed!",
                        console,
                    )
                    exit_fail()
                if BUILD_NAME in extension_settings_data and not check_string(
                    extension_settings_data[BUILD_NAME]
                ):
                    print_error(
                        "extension_settings::build_name uses unsupported characters!",
                        console,
                    )
                    exit_fail()
                parsed_extension_settings = ExtensionSettings(
                    build_legacy=extension_settings_data[BUILD_LEGACY]
                    if BUILD_LEGACY in extension_settings_data
                    else False,
                    build_name=extension_settings_data[BUILD_NAME]
                    if BUILD_NAME in extension_settings_data
                    else None,
                    remove_bl_info=extension_settings_data[REMOVE_BL_INFO]
                    if REMOVE_BL_INFO in extension_settings_data
                    and extension_settings_data[BUILD_LEGACY]
                    else False,
                )

        if INSTALL_VERSIONS in data:
            for ver in data[INSTALL_VERSIONS]:
                if isinstance(ver, float):
                    # Due to some weird conversion bug, we
                    # first turn ver to a string, then make a
                    # decimal from it
                    install_versions.append(Decimal(str(ver)))
                elif isinstance(ver, str):
                    install_versions += version_shorthand_expand(ver)
                else:
                    print_error(f"{ver} isn't a valid floating point value", console)
                    exit_fail()

            if BUILD_EXTENSION in data and data[BUILD_EXTENSION]:
                greater_4_2 = [x for x in install_versions if x >= Decimal("4.2")]
                if not len(greater_4_2):
                    print_error(
                        "When building extensions, 4.2 must be included in install_versions!",
                        console,
                    )
                    exit_fail()

        if BUILD_ACTIONS in data:
            for act in data[BUILD_ACTIONS]:
                if not check_string(act):
                    print_error(f"{act} uses unsupported characters!", console)
                    exit_fail()
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
                        exit_fail()

                    # Add the action to parsed_build_acts to
                    # use later in Config construction
                    parsed_build_acts[act] = BuildAction(
                        script=action_data[SCRIPT] if SCRIPT in action_data else None,
                        ignore_filters=action_data[IGNORE_FILTERS]
                        if IGNORE_FILTERS in action_data
                        else None,
                        depends_on=action_data[DEPENDS_ON]
                        if DEPENDS_ON in action_data
                        else None,
                    )
                    continue

                # If an action has nothing defined, what's the
                # point of said action?
                print_error(f"{act} must have something defined!", console)
                exit_fail()

    except Exception as e:
        console.print(e)
        console.print(traceback.format_exc())
        console.print(data)
        exit_fail()

    return Config(
        addon_folder=data["addon_folder"],
        build_name=data["build_name"],
        build_extension=data[BUILD_EXTENSION] if BUILD_EXTENSION in data else False,
        extension_settings=parsed_extension_settings,
        install_versions=sorted(install_versions, reverse=True)
        if "install_versions" in data
        else None,
        build_actions=parsed_build_acts if len(parsed_build_acts) else None,
        additional_actions=additional_actions,
    )


def version_shorthand_expand(ver: str) -> list[Decimal]:
    """Given a version string, return a list
    of Decimal versions that correspond to the
    shorthand in question.

    Returns:
        list[Decimal] of versions
    """

    versions: list[Decimal] = []
    if ver.count("+") > 0:
        # the + shorthand states to calculate
        # 10 versions above the minimum. Unlike ..,
        # this does not take into account VERSION_JUMPS,
        # in order to encourage developers to also
        # use .. for defining explicit ranges
        split_ver = ver.split("+", 1)

        accumulator = Decimal(split_ver[0])
        versions.append(accumulator)

        # Add one to the max since the first + won't
        # be included in the range, and add one more
        # to make it a proper count of 10
        for i in range(1, (10 * (len(split_ver[1]) + 2))):
            # Due to changes in Blender versioning,
            # we add 0.01 for pre-3.0 (eg. 2.93 -> 2.93)
            # and 0.1 for everything else (eg. 3.0 -> 3.1)
            if accumulator < Decimal(3.0):
                accumulator += Decimal(0.01)
            else:
                accumulator += Decimal(0.1)
            versions.append(accumulator)

    elif ".." in ver:
        # .. gets the ranges of versions between
        # the minimum and maximum. Since we want people
        # to use this (as it defines an explicit range), we
        # also take into account VERSION_JUMPS
        split_ver = ver.split("..")
        accumulator = Decimal(split_ver[0])
        max_ver = Decimal(split_ver[1])
        del split_ver

        versions.append(accumulator)
        while accumulator < max_ver:
            # Due to changes in Blender versioning,
            # we add 0.01 for pre-3.0 (eg. 2.93 -> 2.93)
            # and 0.1 for everything else (eg. 3.0 -> 3.1)
            if accumulator < Decimal(3.0):
                accumulator += Decimal(0.01)
            else:
                accumulator += Decimal(0.1)
            versions.append(accumulator)

            # Jump versions
            #
            # Again due to a weird bug, we
            # use strings for jump keys
            if str(accumulator) in VERSION_JUMPS:
                accumulator = VERSION_JUMPS[str(accumulator)]
    return versions
