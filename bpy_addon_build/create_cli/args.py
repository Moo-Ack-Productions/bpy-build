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

import argparse
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Command(Enum):
    INIT = "init"
    ACTION = "action"


class SubCommand(Enum):
    ADD = "add"


@dataclass
class Args:
    """Arguments for BabEx

    Attributes
    ----------
    command: Command
        The command for BabEx to execute

    subcommand: Optional[SubCommand]
        Subcommand for whatever command is
    """

    command: Command
    subcommand: Optional[SubCommand]


def parse_args() -> Optional[Args]:
    """Parse arguments with argparse and
    returns an Args object.

    Returns:
        - Args if sucessful
        - None if error
    """
    parser = argparse.ArgumentParser(
        prog="BabEx", description="Manage a BpyBuild project"
    )
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    _ = subparsers.add_parser("init", help="Initialize a project")

    parser_action = subparsers.add_parser("action", help="Manage actions in a project")
    action_subparser = parser_action.add_subparsers(
        help="sub-command help", dest="subcommand"
    )
    _ = action_subparser.add_parser("add", help="Add an action to a project")

    args = parser.parse_args()

    if hasattr(args, "command"):
        if args.command == "init":  # type: ignore
            return Args(command=Command.INIT, subcommand=None)
        elif args.command == "action":  # type: ignore
            if hasattr(args, "subcommand"):
                if args.subcommand == "add":  # type: ignore
                    return Args(command=Command.ACTION, subcommand=SubCommand.ADD)
    return None
