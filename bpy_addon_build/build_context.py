from pathlib import Path
from typing import Dict, List
from attrs import define

"""
Context of the build environment, from settings to 
actions to paths, etc.
"""


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@define  # type: ignore
class BuildContext:
    """
    Path of the addon source. By default, it is
    assumed to be at the root of the current working
    directory.
    """

    addon_path: Path = Path(".")
    build_name: str = ""
    install_versions: List[float] = []
    actions: Dict[str, str] = {}
