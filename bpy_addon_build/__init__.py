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
        data: Dict[str, Union[str, List[float], Dict[str, Dict[str, str]]]] = (
            yaml.safe_load(f)
        )
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
