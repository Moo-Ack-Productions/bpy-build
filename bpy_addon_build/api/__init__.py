import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from rich.console import Console

from bpy_addon_build import util
from bpy_addon_build.args import Args
from bpy_addon_build.config import BUILT_IN_ACTS, Config


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
class BpyVariableDef:
    """Class for dynamic BpyBuild variables"""

    # Variable being defined
    variable: str

    # Value of the variable
    vaule: str


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
            self.actions_to_execute: list[str] = []

            current_actions = cli.actions + conf.additional_actions
            if cli.debug_mode:
                print(current_actions)

            # TODO: Figure out a good way to consolidate these two for
            # loops into a single for loop
            #
            # The two loops is weird, and I hate it, but there's no easy
            # way to self-modify a list that is currently being iterated on
            #
            # The first loop handles subactions and adding them to the list.
            # Unlike conf.additional_actions, which is added to the end of the
            # execution list, subactions are to be ran after the parent action,
            # and as such require special handling
            #
            # The second loop is what handles the dependencies, as it is ran on
            # the final execution list, and also loads the scripts in as modules
            for action_name in current_actions:
                if action_name not in self.build_actions:
                    # Continue on, this loop doesn't apply to built-in actions
                    if action_name in BUILT_IN_ACTS:
                        self.actions_to_execute.append(action_name)
                        continue
                    util.print_error(f"{action_name} not defined in config!", console)
                    util.exit_fail()

                # Handle subactions
                action = self.build_actions[action_name]

                self.actions_to_execute.append(action_name)
                if action.subactions:
                    self.actions_to_execute += (
                        action.subactions
                    )  # add subactions after action

            for action_name, action in self.build_actions.items():
                if action_name not in self.actions_to_execute:
                    continue

                if action.depends_on is not None:
                    if debug_mode:
                        print(action, "depends on", action.depends_on)
                    for dep in action.depends_on:
                        if (
                            dep in self.actions_to_execute
                            and self.actions_to_execute.index(dep)
                            < self.actions_to_execute.index(action_name)
                        ):
                            continue
                        util.print_error(
                            f"{dep} required to run {action_name}", console
                        )
                        util.exit_fail()

                if action.script is None:
                    continue

                mod = self.add_modules(cli.path, action_name, debug_mode)
                if mod is None:
                    continue
                self.action_mods[action_name] = mod

    def add_modules(
        self, config_path: Path, action: str, debug_mode: bool
    ) -> ModuleType | None:
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
