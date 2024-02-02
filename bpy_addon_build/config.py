from typing import Dict, List, Optional
from attrs import frozen


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@frozen  # type: ignore
class BuildAction:
    """
    Class that represents a build
    action

    Attributes
    ----------
    script: str
        The Python script associated with the action

    ignore_filters: Optional[List[str]]
        Glob filters to ignore when copying the addon
        folder with this action
    """

    script: str
    ignore_filters: Optional[List[str]] = None


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@frozen  # type: ignore
class Config:
    """
    Class to better handle config parsing, especially with more complex arguments

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
