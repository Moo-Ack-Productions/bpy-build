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

import argparse


def _create_init_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Create the init command"""
    _ = subparsers.add_parser("init", help="Initialize a project")


def _create_action_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Create the action command with its subcommands"""
    parser_action = subparsers.add_parser("action", help="Manage actions in a project")
    action_subparser = parser_action.add_subparsers(
        help="sub-command help", dest="add_subcommand"
    )
    _ = action_subparser.add_parser("add", help="Add an action to a project")


def create_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="BabEx", description="Manage a BpyBuild project"
    )
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")
    _create_init_command(subparsers)
    _create_action_command(subparsers)
    return parser.parse_args()
