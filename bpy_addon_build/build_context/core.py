from __future__ import annotations

from pathlib import Path

from attrs import define
from rich.console import Console

from bpy_addon_build.api import Api
from bpy_addon_build.args import Args
from bpy_addon_build.config import Config

INSTALL_PATHS: list[str] = [
    "~/AppData/Roaming/Blender Foundation/Blender/",
    "~/Library/Application Support/Blender/",
    "~/.config/blender/",
]

# Must be ignored because Mypy likes
# to complain about this for some reason
WORKING_DIR = Path.cwd()  # type: ignore

console = Console()


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@define  # type: ignore
class BuildContext:
    """
    Context of the build environment, from settings to
    actions to paths, etc.

    Attributes
    ----------
    config_path: Path
        Path to config file

    config: Config
        Configuration defined by the user

    cli: Args
        Arguments passed by the user
    """

    config_path: Path
    config: Config
    cli: Args
    api: Api
