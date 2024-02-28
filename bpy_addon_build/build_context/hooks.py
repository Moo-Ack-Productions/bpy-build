from bpy_addon_build.api import BabContext
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
        cwd = Path(ctx.config_path.parent, ctx.config.addon_folder).expanduser()
        os.chdir(cwd)
        for k in ctx.cli.actions:
            build_action_prebuild(ctx, k, console, BabContext(cwd))
        os.chdir(WORKING_DIR)


def run_main_hooks(ctx: BuildContext, stage_one: Path, addon_folder: Path) -> None:
    if len(ctx.cli.actions):
        cwd = stage_one.joinpath(addon_folder.name).expanduser()
        os.chdir(cwd)
        for k in ctx.cli.actions:
            build_action_main(ctx, k, console, BabContext(cwd))
        os.chdir(WORKING_DIR)


def run_preinstall_hooks(ctx: BuildContext, zip_path: Path) -> None:
    if len(ctx.cli.actions):
        cwd = zip_path.expanduser().parent
        os.chdir(cwd)
        for k in ctx.cli.actions:
            build_action_preinstall(ctx, k, console, BabContext(cwd))
            os.chdir(WORKING_DIR)


def run_postinstall_hooks(ctx: BuildContext, v_path: Path) -> None:
    if len(ctx.cli.actions):
        os.chdir(v_path)
        for k in ctx.cli.actions:
            build_action_postinstall(ctx, k, console, BabContext(v_path))
            os.chdir(WORKING_DIR)


def run_cleanup_hooks(ctx: BuildContext) -> None:
    if len(ctx.cli.actions):
        cwd = Path(ctx.config_path.parent, ctx.config.addon_folder).expanduser()
        os.chdir(cwd)
        for k in ctx.cli.actions:
            build_action_cleanup(ctx, k, console, BabContext(cwd))
            os.chdir(WORKING_DIR)
