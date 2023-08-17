import shutil
from pathlib import Path
from typing import Dict, List
from attrs import define, field, Attribute


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
    addon_path: Path
        Path of the addon source. By default, it is
        assumed to be at the root of the current working
        directory.

    build_name: str
        Name of the final build

    install_versions: List[float]
        The versions of Blender that Bpy-Build should
        automatically install to.

    actions: Dict[str, str]
        All action names and the Python files they're
        associated with.
    """

    config_path: Path
    addon_path: Path = field(default=Path("."))
    build_name: str = field(default="")
    install_versions: List[float] = field(default=[])
    actions: Dict[str, str] = field(default={})
    defined_actions: List[str] = field(default=[])

    @install_versions.validator
    def install_versions_check(self, _: Attribute, value: List[float]) -> None:
        """
        Validator for install_versions since isinstance doesn't
        support generics. This iterates through all versions defined
        and checks to see if they're a float. In the future, we may also
        check to see if the version itself is valid.
        """

        for ver in value:
            if not isinstance(ver, float):
                raise ValueError(
                    f"Expected a list of floats for install_versions!, found {ver}"
                )

    @actions.validator
    def action_check(self, _: Attribute, value: Dict[str, str]) -> None:
        """
        Validator for actions since isinstance doesn't
        support generics. This iterates through all key-value
        pairs defined in actions and checks to see if they are
        strings.
        """

        for key in value:
            if not isinstance(key, str):
                raise ValueError(
                    f"Expected a dictionary of strings to strings, found {key} as a key!"
                )
            if not isinstance(value[key], str):
                raise ValueError(
                    f"Expected a dictionary of strings to strings, found {value[key]} as a value!"
                )

    @defined_actions.validator
    def defined_actions_check(self, _: Attribute, value: List[float]) -> None:
        """
        Validator for defined_actions since isinstance doesn't
        support generics. This iterates through all actions defined
        and checks to see if they're a string and are defined in actions
        """

        for act in value:
            if not isinstance(act, str):
                raise ValueError(
                    f"Expected a list of string for defined_actions!, found {act}"
                )
            if act not in self.actions:
                raise Exception(f"{act} is not defined in actions!")

    def build(self) -> None:
        """
        Function that does the actual building.

        Returns:
            None
        """

        # Create some constants
        BUILD_DIR = Path("build")
        STAGE_ONE = BUILD_DIR.joinpath(Path("stage-1"))

        ADDON_FOLDER = self.config_path.parent.joinpath(self.addon_path)

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
            return path.joinpath(Path(self.build_name))

        shutil.copytree(ADDON_FOLDER, combine_with_build(STAGE_ONE))
        if len(self.defined_actions):
            STAGE_TWO = BUILD_DIR.joinpath(Path("stage-2"))
            if not STAGE_TWO.exists():
                STAGE_TWO.mkdir()
            if STAGE_TWO.exists():
                shutil.rmtree(STAGE_TWO)
                STAGE_TWO.mkdir()

            shutil.copytree(
                combine_with_build(STAGE_ONE), combine_with_build(STAGE_TWO)
            )
            for act in self.defined_actions:
                self.action(act, STAGE_TWO.joinpath(ADDON_FOLDER.name))
            shutil.make_archive(str(combine_with_build(BUILD_DIR)), "zip", STAGE_TWO)
        else:
            shutil.make_archive(str(combine_with_build(BUILD_DIR)), "zip", STAGE_ONE)

    def action(self, action: str, folder: Path) -> None:
        """
        Runs an action

        action: string representing the action name
        folder: the root of the addon

        Returns:
            None
        """
        if action in self.actions:
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
                        Path(self.actions[action])
                    ),
                ],
                cwd=folder,
            ).wait()
