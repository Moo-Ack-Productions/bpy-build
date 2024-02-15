from types import ModuleType
from typing import Dict, Optional
from pathlib import Path
from bpy_addon_build.config import Config
from dataclasses import dataclass
import sys


@dataclass
class BpyError:
    msg: str


@dataclass
class BpyWarning:
    msg: str


class Api:
    """
    API object; this holds all scripts used as modules

    Attributes
    ----------
    build_actions: Dict[str, str]
        Action name to script file

    action_mods: Dict[str, ModuleType]
        Action name to module
    """

    def __init__(self, conf: Config, config_path: Path) -> None:
        if conf.build_actions is not None:
            self.build_actions = conf.build_actions
            self.action_mods: Dict[str, ModuleType] = {}

            for action in self.build_actions:
                mod = self.add_modules(config_path, action)
                if mod is None:
                    continue
                self.action_mods[action] = mod

    def add_modules(self, config_path: Path, action: str) -> Optional[ModuleType]:
        import importlib.util

        path = config_path.parent.resolve().joinpath(
            Path(self.build_actions[action].script)
        )
        action_spec = importlib.util.spec_from_file_location(action, path)
        if action_spec is None:
            return None
        action_mod = importlib.util.module_from_spec(action_spec)
        if action_mod is None:
            return None

        sys.modules[action] = action_mod
        if action_spec.loader is not None:
            action_spec.loader.exec_module(action_mod)

        return action_mod
