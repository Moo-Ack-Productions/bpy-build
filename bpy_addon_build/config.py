from typing import Dict, List, Optional
from attrs import frozen


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

    actions: Optional[Dict[str, str]]
        All actions that can occur during the build
    """

    addon_folder: str
    build_name: str
    install_versions: Optional[List[float]]
    build_actions: Optional[Dict[str, str]]
