from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
from . import args
from .build_context import BuildContext


def main() -> None:
    cli: args.Args = args.Args()
    cli.parse_args()
    print(cli)

    if not cli.path.exists():
        print(f"Could not find {str(cli.path)}")

    context: Optional[BuildContext] = None
    with open(cli.path, "r") as f:
        data: Dict[str, Union[str, List[float], Dict[str, str]]] = yaml.safe_load(f)

        # Break down the different options
        # and retrive them from the config
        addon_folder: Optional[str] = None
        build_name: Optional[str] = None
        versions: Optional[List[float]] = None
        actions: Optional[Dict[str, str]] = None

        if isinstance(data["addon_folder"], str):
            addon_folder = data["addon_folder"]
        if isinstance(data["build_name"], str):
            build_name = data["build_name"]
        if isinstance(data["install_versions"], List):
            versions = data["install_versions"]
        if isinstance(data["build_actions"], Dict):
            actions = data["build_actions"]

        if (
            addon_folder is not None
            and build_name is not None
            and versions is not None
            and actions is not None
        ):
            context = BuildContext(Path(addon_folder), build_name, versions, actions)

    print(context)


if __name__ == "__main__":
    main()
