from typing import Callable, Optional, Union, get_type_hints
from typeguard import TypeCheckError, check_type
from bpy_addon_build.api import BabContext, BpyError, BpyWarning
from rich.console import Console

from bpy_addon_build.build_context import BuildContext

ApiFunction = Callable[[BabContext], Optional[Union[BpyWarning, BpyError]]]


def build_action_prebuild(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
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
        func: ApiFunction = ctx.api.action_mods[action].pre_build

        try:
            check_type(func, ApiFunction)
        except TypeCheckError as e:
            console.print(
                f"pre_build function for {action} does not have the correct type signature!",
                style="red",
            )

            # we disable mypy checks here because at this
            # point, we don't care about the type that's
            # returned in get_type_hints, we just want
            # to know the length
            if not len(get_type_hints(func)):  # type: ignore
                console.print(
                    f"Perhaps you are missing type annotations?", style="yellow"
                )
            print(e)

        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)
        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_main(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
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
        func: ApiFunction = ctx.api.action_mods[action].main

        try:
            check_type(func, ApiFunction)
        except TypeCheckError as e:
            console.print(
                f"main function for {action} does not have the correct type signature!",
                style="red",
            )

            # we disable mypy checks here because at this
            # point, we don't care about the type that's
            # returned in get_type_hints, we just want
            # to know the length
            if not len(get_type_hints(func)):  # type: ignore
                console.print(
                    f"Perhaps you are missing type annotations?", style="yellow"
                )
            print(e)

        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_preinstall(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
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
        func: ApiFunction = ctx.api.action_mods[action].pre_install

        try:
            check_type(func, ApiFunction)
        except TypeCheckError as e:
            console.print(
                f"pre_install function for {action} does not have the correct type signature!",
                style="red",
            )

            # we disable mypy checks here because at this
            # point, we don't care about the type that's
            # returned in get_type_hints, we just want
            # to know the length
            if not len(get_type_hints(func)):  # type: ignore
                console.print(
                    f"Perhaps you are missing type annotations?", style="yellow"
                )
            print(e)

        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_postinstall(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
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
        func: ApiFunction = ctx.api.action_mods[action].post_install

        try:
            check_type(func, ApiFunction)
        except TypeCheckError as e:
            console.print(
                f"post_install function for {action} does not have the correct type signature!",
                style="red",
            )

            # we disable mypy checks here because at this
            # point, we don't care about the type that's
            # returned in get_type_hints, we just want
            # to know the length
            if not len(get_type_hints(func)):  # type: ignore
                console.print(
                    f"Perhaps you are missing type annotations?", style="yellow"
                )
            print(e)

        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")


def build_action_cleanup(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
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
        func: ApiFunction = ctx.api.action_mods[action].clean_up

        try:
            check_type(func, ApiFunction)
        except TypeCheckError as e:
            console.print(
                f"clean_up function for {action} does not have the correct type signature!",
                style="red",
            )

            # we disable mypy checks here because at this
            # point, we don't care about the type that's
            # returned in get_type_hints, we just want
            # to know the length
            if not len(get_type_hints(func)):  # type: ignore
                console.print(
                    f"Perhaps you are missing type annotations?", style="yellow"
                )
            print(e)

        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)

        if res is not None:
            if isinstance(res, BpyError):
                console.print(f"{res.msg}", style="red")
                quit(-1)
            elif isinstance(res, BpyWarning):
                console.print(f"{res.msg}", style="yellow")
