# Copyright (c) 2024 Mahid Sheikh <mahid@standingpad.org>. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Dict, List, Optional, Union
import yaml
from bpy_addon_build.api import Api
from bpy_addon_build.build_context import hooks
from bpy_addon_build.build_context.build import build
from bpy_addon_build.build_context.install import install

from bpy_addon_build.config import Config
from . import args
from .build_context import BuildContext
from cattrs.preconf.pyyaml import make_converter
from rich.console import Console


def main() -> None:
    cli = args.parse_args()
    console = Console()
    converter = make_converter()

    if cli.debug_mode:
        console.print(cli)

    if not cli.path.exists():
        print(f"Could not find {str(cli.path)}")

    context: Optional[BuildContext] = None
    with open(cli.path, "r") as f:
        data: Dict[
            str, Union[str, List[float], Dict[str, Dict[str, str]]]
        ] = yaml.safe_load(f)
        config: Config = converter.structure(data, Config)
        api: Api = Api(config, cli.path, cli.debug_mode)
        context = BuildContext(cli.path, config, cli, api)

    if cli.debug_mode:
        console.print(context)
    if not cli.path.parent.joinpath(config.addon_folder).exists():
        print("Addon folder does not exist!")
        return
    build_path = build(context)
    install(context, build_path)
    hooks.run_cleanup_hooks(context)


if __name__ == "__main__":
    main()
