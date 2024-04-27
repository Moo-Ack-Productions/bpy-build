# BSD 3-Clause License
#
# Copyright (c) 2024, Mahid Sheikh
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
from pathlib import Path
from typing import TypedDict

import yaml
from jinja2 import Environment, PackageLoader, select_autoescape
from rich.console import Console
from rich.prompt import Prompt

from bpy_addon_build.build_context.hook_definitions import (
    CLEAN_UP,
    MAIN,
    POST_INSTALL,
    PRE_BUILD,
    PRE_INSTALL,
)
from bpy_addon_build.config import BUILD_ACTIONS, SCRIPT, ConfigDict
from bpy_addon_build.util import EXIT_FAIL, print_error


class GenerateActionDict(TypedDict):
    name: str
    hooks: str


def _generate_action(args: GenerateActionDict) -> None:
    """Generates an action

    This is made a separate function for testing purposes"""
    action_scripts = Path("action-scripts")
    if not action_scripts.exists():
        action_scripts.mkdir()

    script_path = Path(action_scripts, f"{args['name']}.py")
    with open(script_path, "w") as f:
        template_vars = {
            "minor_version": sys.version_info[1],
            PRE_BUILD: PRE_BUILD in args["hooks"],
            MAIN: MAIN in args["hooks"],
            PRE_INSTALL: PRE_INSTALL in args["hooks"],
            POST_INSTALL: POST_INSTALL in args["hooks"],
            CLEAN_UP: CLEAN_UP in args["hooks"],
        }
        env = Environment(
            loader=PackageLoader("bpy_addon_build.create_cli"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )  # type: ignore[misc]
        template = env.get_template("action.py.jinja")  # type: ignore[misc]
        _ = f.write(template.render(template_vars))  # type: ignore[misc]

    with open("bpy-build.yaml", "r+") as f:
        data: ConfigDict = yaml.safe_load(f)
        _ = f.seek(0)
        if BUILD_ACTIONS not in data:
            data[BUILD_ACTIONS] = {}

        data[BUILD_ACTIONS][args["name"]] = {SCRIPT: str(script_path)}
        yaml.dump(data, f)


def create_action() -> None:
    """Create a new BpyBuild action"""
    console = Console()

    if not Path("bpy-build.yaml").exists():
        print_error("Must be in project root!", console)
        sys.exit(EXIT_FAIL)

    action_scripts = Path("action-scripts")
    while True:
        name: str = Prompt.ask("What is the name of this action?", default="my_action")
        if not Path(action_scripts, f"{name}.py").exists():
            break
        print_error(f"{name} already defined!", console)

    while True:
        options = [PRE_BUILD, MAIN, PRE_INSTALL, POST_INSTALL, CLEAN_UP]
        actions: str = Prompt.ask(
            f"List the hooks you want, spaces in between (Options: {options})",
            default=MAIN,
        )

        break_loop = True
        for a in actions.strip().split(", "):
            if a not in options:
                break_loop = False
                print_error(f"{a} is not a valid hook!", console)

        if break_loop:
            break

    _generate_action({"name": name, "hooks": actions})
