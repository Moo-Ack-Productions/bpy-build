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

# Disclaimer: This is not a product from VLK Architects or VLK Experience Design,
# nor is this endorsed by VLK Architects or VLK Experience Design

from __future__ import annotations

import copy
from decimal import getcontext
from typing import Optional

import attrs
import yaml
from rich.console import Console

from bpy_addon_build.api import Api
from bpy_addon_build.build_context import hooks
from bpy_addon_build.build_context.build import build
from bpy_addon_build.build_context.install import install
from bpy_addon_build.config import Config, ConfigDict, build_config

from . import args
from .build_context.core import BuildContext


def main() -> None:
    # Set the precision for Decimal to
    # 3, which corresponds to X.XX
    getcontext().prec = 3

    cli = args.parse_args()
    console = Console()

    if cli.debug_mode:
        console.print(cli)

    if not cli.path.exists():
        print(f"Could not find {str(cli.path)}")

    context: Optional[BuildContext] = None
    with open(cli.path, "r") as f:
        data: ConfigDict = yaml.safe_load(f)
        config: Config = build_config(data)
        api: Api = Api(config, cli, cli.debug_mode)
        context = BuildContext(cli.path, config, cli, api)

        if cli.debug_mode:
            console.print(context)
    if not cli.path.parent.joinpath(config.addon_folder).exists():
        print("Addon folder does not exist!")
        return

    build_path = build(context)
    install(context, build_path)
    hooks.run_cleanup_hooks(context)

    # Build legacy addon alongside extension
    #
    # To reduce as many issues as possible, we
    # treat this as if it were a separate call
    # of BpyBuild but with an altered config
    if (
        (config.build_extension and config.extension_settings is not None)
        and config.extension_settings.build_legacy
        and not cli.build_extension_only
    ):
        # Remove extension action in a copy
        # of additional_actions
        additional_actions = copy.deepcopy(config.additional_actions)
        if "extension" in additional_actions:
            additional_actions.remove("extension")

        override_config = attrs.evolve(
            config,
            build_name=config.build_name + "_legacy",
            build_extension=False,
            extension_settings=None,
            additional_actions=additional_actions,
        )

        override_api: Api = Api(override_config, cli, cli.debug_mode)

        # Change the context object. This is fine
        # since this is ran last
        context.config = override_config
        context.api = override_api

        if cli.debug_mode:
            console.print(override_config)
            console.print(context)
            console.print(context.api.actions_to_execute)

        build_path = build(context)
        install(context, build_path)
        hooks.run_cleanup_hooks(context)


if __name__ == "__main__":
    main()
