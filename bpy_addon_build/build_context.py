import shutil
from pathlib import Path
from typing import Dict, List
from attrs import define, field, Attribute
from bpy_addon_build.args import Args

from bpy_addon_build.config import Config
from rich.console import Console

INSTALL_PATHS: List[str] = [
    "~/AppData/Roaming/Blender Foundation/Blender/{0}/scripts/addons",
    "~/Library/Application Support/Blender/{0}/scripts/addons",
    "~/.config/blender/{0}/scripts/addons",
]


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

    def build(self) -> None:
        """
        Function that does the actual building.

        Returns:
            None
        """

        # Create some constants
        BUILD_DIR = Path("build")
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
        if len(self.cli.actions):
            for k in self.cli.actions:
                self.action(k, STAGE_ONE.joinpath(ADDON_FOLDER.name))
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
        console = Console()
        for v in versions:
            installed = False
            for p in INSTALL_PATHS:
                path = Path(p.format(str(v))).expanduser()
                if not path.exists():
                    # For cases like 2.8, 2.9, etc, check with this method
                    path = Path(p.format(str(format(v, ".2f")))).expanduser()
                    if not path.exists():
                        continue
                else:
                    addon_path = path.joinpath(Path(self.config.build_name))
                    if addon_path.exists():
                        shutil.rmtree(addon_path)
                    shutil.unpack_archive(build_path, path)
                    console.print(f"Installed to {str(path)}", style="green")
                    installed = True
            if not installed:
                console.print(f"Cound not find {v}", style="yellow")

    def action(self, action: str, folder: Path) -> None:
        """
        Runs an action

        action: string representing the action name
        folder: the root of the addon

        Returns:
            None
        """
        if self.config.build_actions is None:
            print("Actions must be defined to use them!")
            return
        if action in self.cli.actions:
            import subprocess

            # We call wait here to make sure
            # that the action has finished in
            # its entirity. Otherwise, the
            # addon will be built with a weird
            # result.
            subprocess.Popen(
                [
                    "python",
                    self.config_path.parent.resolve().joinpath(
                        Path(self.config.build_actions[action].script)
                    ),
                ],
                cwd=folder,
            ).wait()
