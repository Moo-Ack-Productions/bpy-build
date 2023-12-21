import argparse
from pathlib import Path
from typing import List, Optional, cast
from attrs import define, field, Attribute


# Must be ignored to pass Mypy as this has
# an expression of Any, likely due to how
# attrs works
@define  # type: ignore
class Args:
    """
    All arguments defined, converted into their intended
    types to make developer's lives less of a headache.

    Attributes
    ----------
    path: Path
        Path to build configuration; by default set to bpy-build.yaml in
        the current directory.

        -c/--config can replace this path, should the user decide to do so.

    versions: List[float]
        Specific versions the user wants to install too

    actions: List[str]
        The actions that the user wants to execute
    """

    path: Path = field(default=Path("bpy-build.yaml"))
    versions: List[float] = field(default=[])
    actions: List[str] = field(default=["default"])
    debug_mode: bool = field(default=False)

    @path.validator
    def path_validate(self, _: Attribute, value: Path) -> None:
        # Assume the user did not pass
        # a path in
        if value is None:
            return
        if not value.exists():
            raise FileNotFoundError("File does not exist!")
        if value.is_dir():
            raise IsADirectoryError("Expected a file, got a direcory!")

    @versions.validator
    def version_validate(self, _: Attribute, value: List[float]) -> None:
        if value is None:
            self.versions = []
        else:
            for ver in value:
                if not isinstance(ver, float):
                    raise ValueError("Expected List of floating point values!")

    @actions.validator
    def actions_validate(self, _: Attribute, value: List[str]) -> None:
        if value is None:
            self.actions = ["default"]
        else:
            for act in value:
                if not isinstance(act, str):
                    raise ValueError("Expect List of strings!")


def parse_args() -> Args:
    """
    Parses arguments passed in the CLI.

    This uses argparse and creates an Args object
    based on the arguments passed

    This can throw an exception in the following cases:
        - File related
            - The passed config does not exist
            - The passed config is a directory

        - Version related
            - -v/--versions wasn't passed with a list
            - The list passed doesn't contain all floating
              point values

    Returns:
        Args
    """

    from argparse import ArgumentParser, Namespace

    parser = ArgumentParser()
    parser.add_argument("-c", "--config", help="Defines the config file to use")
    parser.add_argument(
        "-v",
        "--versions",
        help="Limits which versions to install to",
        nargs="+",
        type=float,
    )
    parser.add_argument(
        "-b",
        "--build-actions",
        help="Defines what actions to execute",
        nargs="+",
        type=str,
    )
    parser.add_argument(
        "-dbg",
        "--debug-mode",
        help="Activates debug mode to understand what's going on",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    args: Namespace = parser.parse_args()
    config: str = "bpy-build.yaml"
    actions: List[str] = ["default"]

    # The config path can be None
    if cast(Optional[str], args.config) is not None:
        config = args.config

    # This allows the default action to always
    # be executed
    if cast(List[str], args.build_actions) is not None:
        actions += cast(List[str], args.build_actions)

    # We use cast here to prevent Mypy from complaining, the
    # validators should handle the types anyway, if argparse doesn't
    return Args(
        Path(cast(str, config)),
        cast(List[float], args.versions),
        cast(List[str], actions),
        cast(bool, args.debug_mode),
    )
