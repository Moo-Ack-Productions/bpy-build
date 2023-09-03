from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
from . import args
from .build_context import BuildContext


def main() -> None:
    cli = args.parse_args()
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

        if "addon_folder" in data and isinstance(data["addon_folder"], str):
            addon_folder = data["addon_folder"]
        else:
            print("addon_folder must be a string!")
            return
        if "build_name" in data and isinstance(data["build_name"], str):
            build_name = data["build_name"]
        else:
            print("build_name must be a string!")
            return
        if "install_versions" in data and isinstance(data["install_versions"], List):
            versions = data["install_versions"]
            if cli.versions:
                versions = cli.versions
        else:
            print("install_versions must be list of floats!")
            return
        if "build_actions" in data and isinstance(data["build_actions"], Dict):
            actions = data["build_actions"]
        else:
            print("build_actions must be a dictionary of string to string!")
            return

        if (
            addon_folder is not None
            and build_name is not None
            and versions is not None
            and actions is not None
        ):
            try:
                context = BuildContext(
                    cli.path,
                    Path(addon_folder),
                    build_name,
                    versions,
                    actions,
                    cli.actions,
                )
            except ValueError as e:
                print(e)
                return
        else:
            # If somehow we get to this point, something has gone
            # very, very wrong, and there's no way to know what has
            # gone wrong
            print("One of the config options is of an invalid type!")
            return
    print(context)
    context.build()


if __name__ == "__main__":
    main()
