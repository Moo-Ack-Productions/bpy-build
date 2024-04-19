from typing import Dict, List, Optional
from attrs import frozen
from cattrs.preconf.pyyaml import make_converter
import cattrs

from .args import Args


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


def build_config(args: Args, data: Dict) -> Config:
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
        quit()
