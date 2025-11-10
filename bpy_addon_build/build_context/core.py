from __future__ import annotations

import sys
from pathlib import Path

from attrs import define
from rich.console import Console

from bpy_addon_build.api import Api, BpyVariableDef
from bpy_addon_build.args import Args
from bpy_addon_build.config import Config, DynamicType
from bpy_addon_build.util import exit_fail, print_error

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

    dynamic_vars: list[BpyVariableDef]
        Dynamic variables defined in actions
    """

    config_path: Path
    config: Config
    cli: Args
    api: Api
    dynamic_vars: list[BpyVariableDef]


# TODO: Get more general list
POSIX_LIST = ("freebsd", "netbsd", "openbsd")


def create_output_name(ctx: BuildContext) -> str:
    """Create the output name based on the settings provided by the developer

    ctx: Build context

    Returns:
        str
    """

    if ctx.config.build_name is not None:
        return ctx.config.build_name

    elif ctx.config.output_name is not None and ctx.config.output_settings is not None:
        string_format_dict = {}
        output_settings = ctx.config.output_settings

        if output_settings.extension is not None:
            if ctx.config.build_extension:
                string_format_dict["extension"] = output_settings.extension
        if output_settings.legacy is not None:
            if not ctx.config.build_extension:
                string_format_dict["legacy"] = output_settings.legacy
        if sys.platform == "windows" and output_settings.windows is not None:
            string_format_dict["windows"] = output_settings.windows
        if sys.platform == "darwin" and output_settings.osx is not None:
            string_format_dict["osx"] = output_settings.osx
        if sys.platform == "linux" and output_settings.linux is not None:
            string_format_dict["linux"] = output_settings.linux
        if sys.platform.startswith(POSIX_LIST) and output_settings.posix is not None:
            string_format_dict["posix"] = output_settings.posix

        # Now add dynamic variables
        if ctx.config.output_settings.dynamic:
            for name in ctx.dynamic_vars:
                string_format_dict[name.variable] = name.vaule

            for dyn_var, dyn_type in ctx.config.output_settings.dynamic:
                if dyn_type == DynamicType.NOT_REQUIRED:
                    continue
                if dyn_var not in string_format_dict:
                    print_error(
                        f"{dyn_var} is defined as @dynamic_required, yet was not defined in any action!",
                        console,
                    )
                    exit_fail()

        return ctx.config.output_name.format(**string_format_dict)

    return "THIS RESULT SHOULD NOT HAPPEN IF IT DOES REPORT IT ON GITHUB IMMEDIATELY"
