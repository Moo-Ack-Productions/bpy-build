from bpy_addon_build.build_context import BuildContext, WORKING_DIR, console
from bpy_addon_build.build_context.hook_definitions import (
    build_action_cleanup,
    build_action_prebuild,
    build_action_main,
    build_action_postinstall,
    build_action_preinstall,
)
from pathlib import Path
import os


def run_prebuild_hooks(ctx: BuildContext) -> None:
    if len(ctx.cli.actions):
        os.chdir(Path(ctx.config_path.parent, ctx.config.addon_folder).expanduser())
        for k in ctx.cli.actions:
            build_action_prebuild(ctx, k, console)
        os.chdir(WORKING_DIR)


def run_main_hooks(ctx: BuildContext, stage_one: Path, addon_folder: Path) -> None:
    if len(ctx.cli.actions):
        os.chdir(stage_one.joinpath(addon_folder.name).expanduser())
        for k in ctx.cli.actions:
            build_action_main(ctx, k, console)
        os.chdir(WORKING_DIR)


def run_preinstall_hooks(ctx: BuildContext, zip_path: Path) -> None:
    if len(ctx.cli.actions):
        os.chdir(zip_path.expanduser().parent)
        for k in ctx.cli.actions:
            build_action_preinstall(ctx, k, console)
            os.chdir(WORKING_DIR)


def run_postinstall_hooks(ctx: BuildContext, v_path: Path) -> None:
    if len(ctx.cli.actions):
        os.chdir(v_path.expanduser())
        for k in ctx.cli.actions:
            build_action_postinstall(ctx, k, console)
            os.chdir(WORKING_DIR)


def run_cleanup_hooks(ctx: BuildContext, build_folder: Path) -> None:
    if len(ctx.cli.actions):
        os.chdir(build_folder.expanduser())
        for k in ctx.cli.actions:
            build_action_cleanup(ctx, k, console)
            os.chdir(WORKING_DIR)
