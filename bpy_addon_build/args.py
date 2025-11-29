from pathlib import Path
from typing import cast

from attrs import Attribute, define, field

# I am a Lord of the Rings fan, so we'll use ASCII
# art designed to look like the Tegwar script from
# the Elvish languages
BPYBUILD_ASCII_ART = """
                                                    dP"Yb.                                  
                                                     `b   'Yb  db                            
                                                                                             
`Yb d88b d88b   `Yb.d888b   .dP""Yb  `Yb d88b d88b      'Yb   'Yb `Y8888888b. `Yb.d88b d88b  
 88P   8Y   8b   88'    8Y        Yb  88P   8Y   8b      88    88    .dP'      88'   8Y   8b 
 88    8P   88   88     8P        dP  88    8P   88      88    88  ,dP         88    8P   88 
 88  .dP' .dP'   88   ,dP   `YbwwdP   88  .dP' .dP'     .8P   .8P  88     .    88  ,dP  ,dP  
 888888888888b.  88888888b.           888888888888b.               `Yb...dP    88            
 88              88                   88                             `\"""'     88            
.8P             .8P                  .8P                                      .8P
"""


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

    debug_mode: bool
        Enable debug logging

    supress_messages: bool
        Supress BpyBuild output
    """

    path: Path = field(default=Path("bpy-build.yaml"))
    versions: list[float] = field(default=[])
    actions: list[str] = field(default=["default"])
    debug_mode: bool = field(default=False)
    supress_messages: bool = field(default=False)
    build_extension_only: bool = field(default=False)

    @path.validator
    def path_validate(self, _: Attribute, value: Path | None) -> None:
        # Assume the user did not pass
        # a path in
        if value is None:
            return
        if not value.exists():
            raise FileNotFoundError(f"File {value} does not exist!")
        if value.is_dir():
            raise IsADirectoryError("Expected a file, got a direcory!")

    @versions.validator
    def version_validate(self, _: Attribute, value: list[float] | None) -> None:
        if value is None:
            self.versions = []
        else:
            for ver in value:
                if not isinstance(ver, float):
                    raise ValueError("Expected List of floating point values!")

    @actions.validator
    def actions_validate(self, _: Attribute, value: list[str] | None) -> None:
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

    from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
    from importlib.metadata import version

    parser = ArgumentParser(
        description=BPYBUILD_ASCII_ART, formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument("-c", "--config", help="Defines the config file to use")
    parser.add_argument(
        "--version",
        action="version",
        version=f"{BPYBUILD_ASCII_ART}\nBpyBuild Version {version('bpy-addon-build')}",
    )
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
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--supress-output",
        help="Supress all BpyBuild output except for build actions. This does not apply to debug logs",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-be",
        "--build-extension-only",
        help="Only build an extension, if legacy building is enabled",
        default=False,
        action="store_true",
    )

    args: Namespace = parser.parse_args()
    config: str = "bpy-build.yaml"
    actions: list[str] = ["default"]

    # The config path can be None
    if cast(str | None, args.config) is not None:
        config = args.config

    # This allows the default action to always
    # be executed
    if cast(list[str], args.build_actions) is not None:
        actions += cast(list[str], args.build_actions)

    # We use cast here to prevent Mypy from complaining, the
    # validators should handle the types anyway, if argparse doesn't
    return Args(
        Path(cast(str, config)),
        cast(list[float], args.versions),
        actions,
        cast(bool, args.debug_mode),
        cast(bool, args.supress_output),
        cast(bool, args.build_extension_only),
    )
