import os
from enum import Enum
from typing import Callable, cast, get_type_hints

from rich.console import Console
from typeguard import TypeCheckError, check_type

from bpy_addon_build.api import BabContext, BpyError, BpyVariableDef, BpyWarning
from bpy_addon_build.build_context.core import WORKING_DIR, BuildContext
from bpy_addon_build.util import exit_fail, print_error, print_warning

# Function signature of all hooks
ApiFunction = Callable[[BabContext], BpyWarning | BpyError | None]

# Function signature of dynamic_name
DynamicNameFunction = Callable[
    [BabContext], list[BpyVariableDef] | BpyWarning | BpyError | None
]


# Old main function for
# backwards compatibility
OldMain = Callable[[], None]

# All hooks
PRE_BUILD = "pre_build"  # WARN: DEPRECATED
PRE_INTER_COPY = "pre_intermediate_copy"
MAIN = "main"  # WARN: DEPRECATED
IN_INTER_COPY = "in_intermediate_copy"
PRE_INSTALL = "pre_install"  # WARN: DEPRECATED
POST_BUILD = "post_build"
POST_INSTALL = "post_install"
CLEAN_UP = "clean_up"
DYNAMIC_NAME = "dynamic_name"


class APIFunc(Enum):
    CTX_ARG = 0

    """
    This will only work for 
    the main function as a 
    form of backwards compatibility
    """
    NO_ARG = 1


def check_api_func(
    func_name: str, func: ApiFunction | OldMain, action: str, console: Console
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
        if func_name == DYNAMIC_NAME:
            check_type(func, DynamicNameFunction)
        else:
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
    if ctx.config.build_actions is None and len(ctx.api.actions_to_execute):
        print("Actions must be defined to use them!")
        return False
    if action not in ctx.api.actions_to_execute:
        if ctx.cli.debug_mode:
            print("Action not in execution list", action)
        return False
    if action not in ctx.api.action_mods:
        if ctx.cli.debug_mode:
            print("Action not in API! Action:", action)
            console.print(ctx.api.action_mods)
        return False
    return True


def perform_returns(res: BpyWarning | BpyError | None, console: Console) -> None:
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
            exit_fail()
        elif isinstance(res, BpyWarning):
            print_error(res.msg, console)


def build_action_pre_inter_copy(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
    """
    Runs an action's pre_intermediate_copy function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if not check_action(ctx, action, console):
        return
    if (has_pre_build := hasattr(ctx.api.action_mods[action], PRE_BUILD)) or hasattr(
        ctx.api.action_mods[action], PRE_INTER_COPY
    ):
        if has_pre_build:
            print_warning(
                "pre_build hook is deprecated, please swap it out for pre_intermediate_copy",
                console,
            )
            print_warning("pre_build will be removed in BpyBuild 0.7", console)
        func: ApiFunction = ctx.api.action_mods[action].pre_build
        _ = check_api_func(PRE_BUILD, func, action, console)
        res: BpyError | BpyWarning | None = func(api_ctx)
        perform_returns(res, console)


def build_action_in_inter_copy(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
    """
    Runs an action's in_intermediate_copy function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if not check_action(ctx, action, console):
        return
    if (has_main := hasattr(ctx.api.action_mods[action], MAIN)) or hasattr(
        ctx.api.action_mods[action], IN_INTER_COPY
    ):
        if has_main:
            print_warning(
                "main hook is deprecated, please swap it out for in_intermediate_copy",
                console,
            )
            print_warning("main wil be removed in BpyBuild 0.7", console)
        func: ApiFunction | OldMain = ctx.api.action_mods[action].main
        if check_api_func(MAIN, func, action, console) == APIFunc.NO_ARG:
            # Backwards compatibility
            os.chdir(api_ctx.current_path)
            cast(OldMain, func)()
            os.chdir(WORKING_DIR)
        else:
            res: BpyError | BpyWarning | None = cast(ApiFunction, func)(api_ctx)
            perform_returns(res, console)


def build_action_dynamic_name(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
    """
    Runs an action's dynamic_name function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], DYNAMIC_NAME):
        func: DynamicNameFunction = ctx.api.action_mods[action].dynamic_name
        res: list[BpyVariableDef] | BpyError | BpyWarning | None = func(api_ctx)
        if isinstance(res, list):
            # While technically this is unneeded, since actions
            # are defined by the end user (and thus could have
            # errors from improper use of typing/lack of typing),
            # it makes sense to validate anyway
            for name in res:
                if isinstance(name, BpyVariableDef):
                    continue
                print_error(
                    "dynamic_name must return a list of only BpyVariableDef!", console
                )
                exit_fail()
            ctx.dynamic_vars = res
        else:
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
        print_warning("pre_install is deprecated, consider using post_build", console)
        print_warning("pre_install will be removed in BpyBuild 0.7", console)
        print_warning(
            "Note: post_build will only run once, and not once for each Blender version",
            console,
        )
        func: ApiFunction = ctx.api.action_mods[action].pre_install
        _ = check_api_func(PRE_INSTALL, func, action, console)
        res: BpyError | BpyWarning | None = func(api_ctx)
        perform_returns(res, console)


def build_action_postbuild(
    ctx: BuildContext, action: str, console: Console, api_ctx: BabContext
) -> None:
    """
    Runs an action's post_build function

    ctx: Build context
    action: string representing the action name
    console: Console from Rich

    Returns:
        None
    """
    if not check_action(ctx, action, console):
        return
    if hasattr(ctx.api.action_mods[action], POST_BUILD):
        func: ApiFunction = ctx.api.action_mods[action].post_build
        _ = check_api_func(PRE_INSTALL, func, action, console)
        res: BpyError | BpyWarning | None = func(api_ctx)
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
        res: BpyError | BpyWarning | None = func(api_ctx)
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
        res: BpyError | BpyWarning | None = func(api_ctx)
        perform_returns(res, console)
