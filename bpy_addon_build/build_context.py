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

    def build(self) -> None:
        """
        Function that does the actual building.

        Returns:
            None
        """

        # Create some constants
        BUILD_DIR = Path("build")
        SUB_DIR = BUILD_DIR.joinpath(Path("subdir"))

        ADDON_FOLDER = self.config_path.parent.joinpath(self.addon_path)

        if not BUILD_DIR.exists():
            BUILD_DIR.mkdir()
        if not SUB_DIR.exists():
            SUB_DIR.mkdir()

        shutil.copytree(ADDON_FOLDER, SUB_DIR.joinpath(Path(self.build_name)))
