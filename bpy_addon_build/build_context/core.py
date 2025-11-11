from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Literal

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


class ExprType(Enum):
    CONST = 0
    VAR = 1
    FALLBACK = 2
    CONCAT = 3
    PAREN = 4
    UNDEFINED = 5


def format_string(input: str, defined_vars: dict[str, str]) -> str:
    """Format the input string with all variables and expressions evaluated

    input: str
        Raw input string

    defined_vars: dict[str, str]
        All variables that are defined

    Returns:
        str - the final string with all expressions evaluated and variables replaced
    """
    constructed_string = ""
    idx = 0
    while idx < len(input):
        char = input[idx]
        match char:
            case "{":
                res_ops, end_idx = parse_expr(input[idx + 1 :])
                res_val = evaluate_expr(res_ops, defined_vars)
                idx += (
                    1 + end_idx
                )  # Add because for parsing, we slice the list from idx+1
                constructed_string += res_val
            case "}":
                print_error(
                    "Encountered } without matching { at index " + str(idx), console
                )
                exit_fail()
            case _:
                constructed_string += char
        idx += 1

    return constructed_string


def evaluate_expr(
    operations: list[tuple[str, ExprType]], defined_vars: dict[str, str]
) -> str:
    """Evaluate the parsed operations from an expression

    operations: list[tuple[str, ExprType]]
        All operations to perform. They must be in a form similar to RPN

    defined_vars: dict[str, str]
        All defined variables

    Returns:
        str - the final result of the expression, if defined
    """
    stack: list[tuple[str, ExprType]] = []

    for val, op in operations:
        match op:
            case ExprType.CONST:
                stack.append((val, op))
            case ExprType.VAR:
                if val not in defined_vars:
                    # Keep the variable name for errors
                    stack.append((val, ExprType.UNDEFINED))
                else:
                    stack.append((defined_vars[val], ExprType.CONST))
            case ExprType.CONCAT:
                right_val, right_type = stack.pop()
                left_val, left_type = stack.pop()

                # If one side is undefined, the whole expression is undefined
                if left_type == ExprType.UNDEFINED or right_type == ExprType.UNDEFINED:
                    stack.append((f"{left_val + right_val}", ExprType.UNDEFINED))
                else:
                    # Variables will have been evaluated, so this will be
                    # a constant
                    stack.append((left_val + right_val, ExprType.CONST))
            case ExprType.FALLBACK:
                right_val, right_type = stack.pop()
                left_val, left_type = stack.pop()

                if left_type == ExprType.UNDEFINED:
                    stack.append((right_val, right_type))

                # If the right side is undefined, then this will
                # simply pushed an undefined value.
                #
                # So the expression:
                #
                # x | y | z
                #
                # Where x and y are undefined will cause the undefined
                # value for y to be pushed, and x to be ignored.
                else:
                    stack.append((left_val, left_type))
            case _:
                print_error(
                    f"Expected variable, constant string, +, or |, got {val}", console
                )
                exit_fail()

    top_val, top_type = stack.pop()
    if top_type != ExprType.CONST:
        print_error(
            f"Expected final evaluated expression to be a constant, got {top_val} {top_type} (please report to GitHub if you think this is incorrect)",
            console,
        )
        exit_fail()
    return top_val


def parse_expr(input: str) -> tuple[list[tuple[str, ExprType]], int]:
    """Parse expression inside {} and convert to something easily evaluable

    This uses an adapted form of the shunting yard algorithm (which is used in
    calculators to convert postfix notation for math into RPN, while preserving
    order of operations). In this version, | (fallback) has a lower precedence
    than + (concatenation), so it clears out the operation stack.

    input: str
        String, must not start with {

    Returns:
        list[tuple[str, ExprType]] - operations in a form akin to RPN
        int - index of last parse value
    """
    expr_op_stack: list[ExprType] = []
    expr_var_const_stack: list[tuple[str, ExprType]] = []

    # Restrict to just these 2 types
    cur_expr_type: Literal[ExprType.VAR, ExprType.CONST] = ExprType.VAR
    cur_idx = 0
    last_char_op = False
    found_r_brace = False
    for idx, char in enumerate(input):
        cur_idx = idx
        match char:
            case "|":
                # Clear entire stack
                #
                # All | have the same precedence, so it's evaluated
                # from left to right
                expr_var_const_stack += [("", op) for op in reversed(expr_op_stack)]
                expr_op_stack = [ExprType.FALLBACK]
                last_char_op = True
            case "+":
                expr_op_stack.append(ExprType.CONCAT)
                last_char_op = True
            case "(":
                expr_op_stack.append(ExprType.PAREN)
                last_char_op = True
            case ")":
                top = expr_op_stack.pop()
                while top != ExprType.PAREN:
                    expr_var_const_stack.append(("", top))
                    top = expr_op_stack.pop()
                last_char_op = True
            case "}":
                # Clear stack
                expr_var_const_stack += [("", op) for op in reversed(expr_op_stack)]
                expr_op_stack.clear()

                # Break from loop
                found_r_brace = True
                break
            case "'" | '"':
                if cur_expr_type == ExprType.CONST:
                    # Special handling for empty strings
                    if not len(expr_var_const_stack):
                        expr_var_const_stack.append(("", ExprType.CONST))
                    else:
                        _, top_type = expr_var_const_stack[-1]
                        if top_type != ExprType.CONST:
                            expr_var_const_stack.append(("", ExprType.CONST))
                    cur_expr_type = ExprType.VAR
                else:
                    cur_expr_type = ExprType.CONST
            case ' ' | '\n':
                # Ignore whitespace
                continue
            case _:
                string, string_type = "", cur_expr_type

                # Add to current top of the stack
                if len(expr_var_const_stack) and not last_char_op:
                    str_top, str_top_type = expr_var_const_stack.pop()

                    # i.e. we're not on a new expression
                    if str_top_type == cur_expr_type:
                        string = str_top

                # Add character and append back to stack
                string += char
                expr_var_const_stack.append((string, string_type))
                last_char_op = False

    if not found_r_brace:
        print_error("No matching } for {", console)
        exit_fail()
    return (expr_var_const_stack, cur_idx)
