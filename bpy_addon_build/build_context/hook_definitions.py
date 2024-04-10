from enum import Enum
import os
from typing import Callable, Optional, Union, cast, get_type_hints
from typeguard import TypeCheckError, check_type
from bpy_addon_build.api import BabContext, BpyError, BpyWarning
from rich.console import Console

from bpy_addon_build.build_context.core import WORKING_DIR, BuildContext
from bpy_addon_build.util import print_error, print_warning

# Function signature of all hooks
ApiFunction = Callable[[BabContext], Optional[Union[BpyWarning, BpyError]]]

# Old main function for
# backwards compatibility
OldMain = Callable[[], None]

# All hooks
PRE_BUILD = "pre_build"
MAIN = "main"
PRE_INSTALL = "pre_install"
POST_INSTALL = "post_install"
CLEAN_UP = "clean_up"


class APIFunc(Enum):
    CTX_ARG = 0

    """
    This will only work for 
    the main function as a 
    form of backwards compatibility
    """
    NO_ARG = 1


def check_api_func(
    func_name: str, func: Union[ApiFunction, OldMain], action: str, console: Console
) -> APIFunc:
    """
    Check type signature of API functions and throw an
    exception if the type signature is incorrect.

    func_name: Name of the function
    func: Function to check
    action: Name of the action
    console: Console from Rich

    Returns:
        None
    """
    try:
        check_type(func, ApiFunction)
        return APIFunc.CTX_ARG
    except TypeCheckError:
        try:
            # check for old main function
            # type signature for backwards
            # compatibility
            check_type(func, OldMain)
            return APIFunc.NO_ARG
        except TypeCheckError:
            pass
        print_error(
            f"{func_name} function for {action} does not have the correct type signature!",
            console,
        )

        # we disable mypy checks here because at this
        # point, we don't care about the type that's
        # returned in get_type_hints, we just want
        # to know the length
        if not len(get_type_hints(func)):  # type: ignore
            print_warning("Perhaps you are missing type annotations?", console)
        raise


def check_action(ctx: BuildContext, action: str, console: Console) -> bool:
    """
    Perform checks on the passed function

    ctx: Build context
    action: action name
    console: Console from Rich

    Returns:
        True if all checks pass,
        False otherwise
    """
    if ctx.config.build_actions is None and len(ctx.cli.actions):
        print("Actions must be defined to use them!")
        return False
    if action not in ctx.cli.actions:
        return False
    if action not in ctx.api.action_mods:
        if ctx.cli.debug_mode:
            print("Action not in API! Action:", action)
            console.print(ctx.api.action_mods)
        return False
    return True


def perform_returns(
    res: Optional[Union[BpyWarning, BpyError]], console: Console
) -> None:
    """
    Performs tasks based on the return value of an API function.

    res: return value from API funcion
    console: Console from Rich

    Returns:
        None
    """
    if res is not None:
        if isinstance(res, BpyError):
            print_error(res.msg, console)
            quit(-1)
        elif isinstance(res, BpyWarning):
            print_error(res.msg, console)


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
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], PRE_BUILD):
        func: ApiFunction = ctx.api.action_mods[action].pre_build
        _ = check_api_func(PRE_BUILD, func, action, console)
        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)
        perform_returns(res, console)


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
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], MAIN):
        func: Union[ApiFunction, OldMain] = ctx.api.action_mods[action].main
        if check_api_func(MAIN, func, action, console) == APIFunc.NO_ARG:
            # Backwards compatibility
            os.chdir(api_ctx.current_path)
            cast(OldMain, func)()
            os.chdir(WORKING_DIR)
        else:
            res: Optional[Union[BpyError, BpyWarning]] = cast(ApiFunction, func)(
                api_ctx
            )
            perform_returns(res, console)


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
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], PRE_INSTALL):
        func: ApiFunction = ctx.api.action_mods[action].pre_install
        _ = check_api_func(PRE_INSTALL, func, action, console)
        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)
        perform_returns(res, console)


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
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], POST_INSTALL):
        func: ApiFunction = ctx.api.action_mods[action].post_install
        _ = check_api_func(POST_INSTALL, func, action, console)
        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)
        perform_returns(res, console)


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
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], CLEAN_UP):
        func: ApiFunction = ctx.api.action_mods[action].clean_up
        _ = check_api_func(CLEAN_UP, func, action, console)
        res: Optional[Union[BpyError, BpyWarning]] = func(api_ctx)
        perform_returns(res, console)
