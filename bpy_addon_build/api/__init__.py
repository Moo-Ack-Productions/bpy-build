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

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import ModuleType

from typing_extensions import override

from bpy_addon_build.config import Config
from bpy_addon_build.util import EXIT_FAIL


class PrintAs(Enum):
    ERROR = 0
    WARNING = 1
    TIP = 2


class BabErrorBase(object):
    """Base objects for stuff that
    prints to standard output"""

    def __init__(self, msg: str) -> None:
        self.msg = msg

    def message_to_print(self) -> tuple[str, PrintAs]:
        """The message to print"""
        return self.msg, PrintAs.ERROR

    def on_exit(self) -> None:
        """What to do afterwards"""
        return


class BpyError(BabErrorBase):
    """Error object for BpyBuild"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

    @override
    def on_exit(self) -> None:
        sys.exit(EXIT_FAIL)


class BpyWarning(BabErrorBase):
    """Warning object for BpyBuild"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

    @override
    def message_to_print(self) -> tuple[str, PrintAs]:
        return self.msg, PrintAs.WARNING


class BpyTip(BabErrorBase):
    """Tip object for BpyBuild"""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

    @override
    def message_to_print(self) -> tuple[str, PrintAs]:
        return self.msg, PrintAs.TIP


@dataclass
class BabContext:
    # Path where the action is being
    # executed in. This should be
    # the intended cwd
    current_path: Path


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

    def __init__(self, conf: Config, config_path: Path, debug_mode: bool) -> None:
        if conf.build_actions is not None:
            self.build_actions = conf.build_actions
            self.action_mods: dict[str, ModuleType] = {}

            for action in self.build_actions:
                if self.build_actions[action].script is None:
                    continue
                mod = self.add_modules(config_path, action, debug_mode)
                if mod is None:
                    continue
                self.action_mods[action] = mod

    def add_modules(
        self, config_path: Path, action: str, debug_mode: bool
    ) -> ModuleType | None:
        import importlib.util

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
        action_mod: ModuleType | None = importlib.util.module_from_spec(action_spec)
        if action_mod is None:
            if debug_mode:
                print("Can not generate module from spec for", action)
                print("Path:", path)
            return None

        sys.modules[action] = action_mod
        if action_spec.loader is not None:
            action_spec.loader.exec_module(action_mod)

        return action_mod
