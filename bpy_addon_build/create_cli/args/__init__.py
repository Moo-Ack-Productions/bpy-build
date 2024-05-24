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

from argparse import Namespace

from bpy_addon_build.create_cli.args import command_classes as cc
from bpy_addon_build.create_cli.args import create_arguments as ca


def parse_args() -> cc.Args | None:
    """Parse arguments with argparse and
    returns an Args object.

    Returns:
        - Args if sucessful
        - None if error
    """

    args = ca.create_arguments()
    if hasattr(args, "command"):
        if args.command == "init":  # type: ignore[misc]
            return cc.Args(command=cc.Command.INIT, args=parse_flags(args))
        elif args.command == "action":  # type: ignore[misc]
            if hasattr(args, "add_subcommand"):
                if args.add_subcommand == "add":  # type: ignore[misc]
                    return cc.Args(
                        command=cc.Command.ACTION, subcommand=cc.SubCommand.ADD, args=[]
                    )
    return None


def parse_flags(args: Namespace) -> list[cc.SubCommandFlags]:
    """Parse arguments for flags to commands

    Returns:
        list[cc.SubCommadnFlags]
    """
    if args.command == "init":  # type: ignore [misc]
        return [cc.InitFlags.IN_PLACE] if args.in_place else []  # type: ignore[misc]
    return []
