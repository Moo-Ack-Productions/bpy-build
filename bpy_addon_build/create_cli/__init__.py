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

from typing import cast

from rich.console import Console

from bpy_addon_build.create_cli.action import create_action
from bpy_addon_build.create_cli.args import command_classes as cc
from bpy_addon_build.create_cli.args import parse_args
from bpy_addon_build.create_cli.project import create_project
from bpy_addon_build.util import print_error


def main() -> None:
    """BabEx entry point

    BabEx (a play on Bab and FedEx) is a tool to manage
    BpyBuild projects. It allows creation of a new project,
    adding actions, etc, handling boilerplate and configuration
    and making everything easier in general.
    """

    args = parse_args()
    console = Console()
    if args is None:
        print_error("Invalid command", console)
        return
    if args.command == cc.Command.INIT:
        create_project(cast(list[cc.InitFlags], args.args))
    elif args.command == cc.Command.ACTION:
        if args.subcommand == cc.SubCommand.ADD:
            create_action()
        else:
            print_error("Invalid command {}", console)


if __name__ == "__main__":
    main()
