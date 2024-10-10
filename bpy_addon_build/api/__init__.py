from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Optional

from rich.console import Console

from bpy_addon_build import util
from bpy_addon_build.args import Args
from bpy_addon_build.config import Config


@dataclass
class BpyError:
    """Error object for BpyBuild"""

    # Message to print in the console
    msg: str


@dataclass
class BpyWarning:
    """Warning object for BpyBuild"""

    # Message to print in the console
    msg: str


@dataclass
class BabContext:
    # Path where the action is being
    # executed in. This should be
    # the intended cwd
    current_path: Path

    # Is the addon currently being
    # build an extension?
    is_extension: bool

    # BpyBuild Config; For built-in
    # actions to use
    builtin_config: Config


class Api:
    """
    API object; this holds all scripts used as modules

    Attributes
    ----------
    build_actions: dict[str, str]
        Action name to script file

    action_mods: dict[str, ModuleType]
        Action name to module
    """

    def __init__(self, conf: Config, cli: Args, debug_mode: bool) -> None:
        console = Console()
        if conf.build_actions is not None:
            self.build_actions = conf.build_actions
            self.action_mods: dict[str, ModuleType] = {}
            self.actions_to_execute: list[str] = cli.actions + conf.additional_actions

            if cli.debug_mode:
                print(self.actions_to_execute)

            for action in self.build_actions:
                if action not in self.actions_to_execute:
                    continue

                depends = self.build_actions[action].depends_on
                if depends is not None:
                    if debug_mode:
                        print(action, "depends on", depends)
                    for dep in depends:
                        if (
                            dep in self.actions_to_execute
                            and self.actions_to_execute.index(dep)
                            < self.actions_to_execute.index(action)
                        ):
                            continue
                        util.print_error(f"{dep} required to run {action}", console)
                        util.exit_fail()

                if self.build_actions[action].script is None:
                    continue

                mod = self.add_modules(cli.path, action, debug_mode)
                if mod is None:
                    continue
                self.action_mods[action] = mod

    def add_modules(
        self, config_path: Path, action: str, debug_mode: bool
    ) -> Optional[ModuleType]:
        script = self.build_actions[action].script
        if script is None:
            return None

        path = config_path.parent.resolve().joinpath(Path(script))

        # Add the parent folder of the script to the sys path
        # so that we don't get module errors
        #
        # While we could argue that developers should at least
        # opt in by calling this themselves, I think automatically
        # doing this isn't a problem for now
        sys.path.append(str(path.expanduser().parent))
        action_spec = importlib.util.spec_from_file_location(action, path)
        if action_spec is None:
            if debug_mode:
                print("Can not generate action spec for", action)
                print("Path:", path)
            return None
        action_mod = importlib.util.module_from_spec(action_spec)
        if action_mod is None:
            if debug_mode:
                print("Can not generate module from spec for", action)
                print("Path:", path)
            return None

        sys.modules[action] = action_mod
        if action_spec.loader is not None:
            action_spec.loader.exec_module(action_mod)

        return action_mod
