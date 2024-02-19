from typing import Optional, Union
from bpy_addon_build.api import BpyError, BpyWarning
from rich.console import Console

from bpy_addon_build.build_context import BuildContext


def build_action_prebuild(ctx: BuildContext, action: str, console: Console) -> None:
    """
    Runs an action's pre_build function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return
    if action not in ctx.cli.actions:
        return
    if action not in ctx.api.action_mods:
        print("Action not in API!")
        return
    if hasattr(ctx.api.action_mods[action], "pre_build"):
        res: Optional[Union[BpyError, BpyWarning]] = ctx.api.action_mods[
            action
        ].pre_build()

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_main(ctx: BuildContext, action: str, console: Console) -> None:
    """
    Runs an action's main function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return
    if action not in ctx.cli.actions:
        return
    if action not in ctx.api.action_mods:
        print("Action not in API!")
        return
    if hasattr(ctx.api.action_mods[action], "main"):
        res: Optional[Union[BpyError, BpyWarning]] = ctx.api.action_mods[action].main()

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_preinstall(ctx: BuildContext, action: str, console: Console) -> None:
    """
    Runs an action's pre_install function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return
    if action not in ctx.cli.actions:
        return
    if action not in ctx.api.action_mods:
        print("Action not in API!")
        return
    if hasattr(ctx.api.action_mods[action], "pre_install"):
        res: Optional[Union[BpyError, BpyWarning]] = ctx.api.action_mods[
            action
        ].pre_install()

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_postinstall(ctx: BuildContext, action: str, console: Console) -> None:
    """
    Runs an action's post_install function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return
    if action not in ctx.cli.actions:
        return
    if action not in ctx.api.action_mods:
        print("Action not in API!")
        return
    if hasattr(ctx.api.action_mods[action], "post_install"):
        res: Optional[Union[BpyError, BpyWarning]] = ctx.api.action_mods[
            action
        ].post_install()

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_cleanup(ctx: BuildContext, action: str, console: Console) -> None:
    """
    Runs an action's clean_up function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return
    if action not in ctx.cli.actions:
        return
    if action not in ctx.api.action_mods:
        print("Action not in API!")
        return
    if hasattr(ctx.api.action_mods[action], "clean_up"):
        res: Optional[Union[BpyError, BpyWarning]] = ctx.api.action_mods[
            action
        ].clean_up()

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")
