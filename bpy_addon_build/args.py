from pathlib import Path
from typing import List, cast
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
    """

    path: Path = field(default=Path("bpy-build.yaml"))
    versions: List[float] = field(default=[])

    @path.validator
    def path_validate(self, _: Attribute, value: Path) -> None:
        if not value.exists():
            raise FileNotFoundError("File does not exist!")
        if value.is_dir():
            raise IsADirectoryError("Expected a file, got a direcory!")

    @versions.validator
    def version_validate(self, _: Attribute, value: List[float]) -> None:
        for ver in value:
            if not isinstance(ver, float):
                raise ValueError("Expected List of floating point values!")


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

    args: Namespace = parser.parse_args()

    # We use cast here to prevent Mypy from complaining, the
    # validators should handle the types anyway, if argparse doesn't
    return Args(Path(cast(str, args.config)), cast(List[float], args.versions))
