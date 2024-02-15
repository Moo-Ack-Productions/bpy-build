import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from attrs import define, field, Attribute
from bpy_addon_build.api import Api, BpyError, BpyWarning
from bpy_addon_build.args import Args

from bpy_addon_build.config import Config
from rich.console import Console

from bpy_addon_build.hooks import (
    build_action_main,
    build_action_postinstall,
    build_action_prebuild,
)

INSTALL_PATHS: List[str] = [
    "~/AppData/Roaming/Blender Foundation/Blender/{0}/scripts/addons",
    "~/Library/Application Support/Blender/{0}/scripts/addons",
    "~/.config/blender/{0}/scripts/addons",
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

    def build(self) -> None:
        """
        Function that does the actual building.

        Returns:
            None
        """

        # Create some constants
        BUILD_DIR = self.config_path.parent / Path("build")
        STAGE_ONE = BUILD_DIR.joinpath(Path("stage-1"))
        FILTERS = []

        # Get all filters from currently used actions
        if self.config.build_actions:
            for i in self.config.build_actions:
                act = self.config.build_actions[i]
                if act.ignore_filters and i in self.cli.actions:
                    FILTERS += act.ignore_filters

        ADDON_FOLDER = self.config_path.parent.joinpath(self.config.addon_folder)

        if not BUILD_DIR.exists():
            BUILD_DIR.mkdir()
        if not STAGE_ONE.exists():
            STAGE_ONE.mkdir()
        if STAGE_ONE.exists():
            shutil.rmtree(STAGE_ONE)
            STAGE_ONE.mkdir()

        def combine_with_build(path: Path) -> Path:
            """
            Local function to get the path with build name.

            We don't need to have a variable for every single
            path, let's just make a function to handle that.

            path: Path you want to add on to

            Returns:
                New path pointing to path/self.build_name
            """
            return path.joinpath(Path(self.config.build_name))

        self.build_action_prebuild()
        # For some weird reason, shutil.ignore_patterns
        # expects positional arguments for all patterns,
        # and not a list like most would expect.
        #
        # Sigh...
        #
        # Due to weirdness of the ignore argument, we also
        # need to add an ignore comment for Mypy
        shutil.copytree(
            ADDON_FOLDER,
            combine_with_build(STAGE_ONE),
            ignore=shutil.ignore_patterns(*FILTERS),  # type: ignore
        )

        self.build_action_main(STAGE_ONE, ADDON_FOLDER)
        shutil.make_archive(str(combine_with_build(BUILD_DIR)), "zip", STAGE_ONE)
        self.install(Path(str(combine_with_build(BUILD_DIR)) + ".zip"))

    def install(self, build_path: Path) -> None:
        """
        Installs the addon to the specified Blender
        versions

        build_path: Path to the built addon

        Returns:
            None
        """
        if self.config.install_versions is None:
            return
        versions = (
            self.cli.versions
            if len(self.cli.versions)
            else self.config.install_versions
        )
        for v in versions:
            installed = False
            for p in INSTALL_PATHS:
                path = Path(p.format(str(v))).expanduser()
                if not path.exists():
                    # For cases like 2.8, 2.9, etc, check with this method
                    path = Path(p.format(str(format(v, ".2f")))).expanduser()
                    if not path.exists():
                        continue
                addon_path = path.joinpath(Path(self.config.build_name))
                if addon_path.exists():
                    shutil.rmtree(addon_path)
                shutil.unpack_archive(build_path, path)
                if not self.cli.supress_messages:
                    console.print(f"Installed to {str(path)}", style="green")
                installed = True
                self.build_action_postinstall(path)
            if not installed and not self.cli.supress_messages:
                console.print(f"Cound not find {v}", style="yellow")

    def build_action_prebuild(self) -> None:
        if len(self.cli.actions):
            os.chdir(
                Path(self.config_path.parent, self.config.addon_folder).expanduser()
            )
            for k in self.cli.actions:
                build_action_prebuild(self, k, console)
            os.chdir(WORKING_DIR)

    def build_action_main(self, stage_one: Path, addon_folder: Path) -> None:
        if len(self.cli.actions):
            os.chdir(stage_one.joinpath(addon_folder.name).expanduser())
            for k in self.cli.actions:
                build_action_main(self, k, console)
            os.chdir(WORKING_DIR)

    def build_action_preinstall(self) -> None:
        pass

    def build_action_postinstall(self, v_path: Path) -> None:
        if len(self.cli.actions):
            os.chdir(v_path.expanduser())
            for k in self.cli.actions:
                build_action_postinstall(self, k, console)
                os.chdir(WORKING_DIR)
