import sys
from pathlib import Path

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


def create_action() -> None:
    """Create a new BpyBuild action"""
    console = Console()

    if not Path("bpy-build.yaml").exists():
        print_error("Must be in project root!", console)
        sys.exit(EXIT_FAIL)

    action_scripts = Path("action-scripts")
    while True:
        name = Prompt.ask("What is the name of this action?", default="my_action")
        if not Path(action_scripts, f"{name}.py").exists():
            break
        print_error(f"{name} already defined!", console)

    while True:
        options = [PRE_BUILD, MAIN, PRE_INSTALL, POST_INSTALL, CLEAN_UP]
        actions = Prompt.ask(
            f"List the hooks you want, spaces in between (Options: {options})",
            default=MAIN,
        )

        break_loop = True
        for a in actions.strip().split(" "):
            if a not in options:
                break_loop = False
                print_error(f"{a} is not a valid hook!", console)

        if break_loop:
            break

    if not action_scripts.exists():
        action_scripts.mkdir()

    script_path = Path(action_scripts, f"{name}.py")
    with open(script_path, "w") as f:
        template_vars = {
            "minor_version": sys.version_info[1],
            PRE_BUILD: PRE_BUILD in actions,
            MAIN: MAIN in actions,
            PRE_INSTALL: PRE_INSTALL in actions,
            POST_INSTALL: POST_INSTALL in actions,
            CLEAN_UP: CLEAN_UP in actions,
        }
        env = Environment(
            loader=PackageLoader("bpy_addon_build.create_cli"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )  # type: ignore
        template = env.get_template("action.py.jinja")  # type: ignore
        _ = f.write(template.render(template_vars))  # type: ignore

    with open("bpy-build.yaml", "r+") as f:
        data: ConfigDict = yaml.safe_load(f)
        _ = f.seek(0)
        if BUILD_ACTIONS not in data:
            data[BUILD_ACTIONS] = {}

        data[BUILD_ACTIONS][name] = {SCRIPT: str(script_path)}
        yaml.dump(data, f)
