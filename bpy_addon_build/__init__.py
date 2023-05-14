import argparse
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List
from rich.console import Console

from . import yaml_conf

WORKING_DIR: Path = Path(os.getcwd())

# All file paths on Windows, MacOS, and Linux based on the Blender Docs
# We use ~ for user directories, and we expand these later on in the code
BLENDER_ADDON_DIR: List[str] = [
    "~/AppData/Roaming/Blender Foundation/Blender/{0}/scripts/addons",
    "~/Library/Application Support/Blender/{0}/scripts/addons",
    "~/.config/blender/{0}/scripts/addons",
]
console = Console()


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Build Blender addons 10 times faster",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version 0.1.0"
    )
    parser.add_argument(
        "--during-build",
        action="store",
        dest="db",
        help="Defines an action to do in addition to default",
    )
    parser.add_argument("files", nargs="*")
    return parser


def parse_file(file: Path) -> yaml_conf.BpyBuildYaml:
    with open(file, "r") as f:
        yaml_config: yaml_conf.BpyBuildYaml = yaml_conf.BpyBuildYaml(f, file)
        return yaml_config


def execute_action(action: Dict[str, str], inter_dir: Path):
    if "create_file" in action:
        file_path = inter_dir / Path(action["create_file"])
        with open(file_path, "w") as f:
            f.write("")


def main():
    parser = init_argparse()
    args = parser.parse_args()
    bpy_build_yaml: Path = WORKING_DIR / Path("bpy-build.yaml")

    if not args.files:
        if bpy_build_yaml.exists():
            pass
        else:
            console.print(
                "Can't find bpy-build.yaml, maybe pass it directly?", style="bold red"
            )
            return
    else:
        for file in args.files:
            bpy_build_yaml = Path(file).resolve()
            break

    yaml_conf = parse_file(bpy_build_yaml)
    build_dir = bpy_build_yaml.parents[0] / Path("build")
    built_zip = build_dir / Path(yaml_conf.build_name + ".zip")

    # Check if the addon folder exists
    if not yaml_conf.addon_folder.exists():
        console.print(
            f"Addon folder {str(yaml_conf.addon_folder)} does not exist!",
            style="bold red",
        )
        return

    # Create build directory so we don't get errors
    if not build_dir.exists():
        build_dir.mkdir()

    # Remove the built zip so we don't get errors
    if built_zip.exists():
        os.remove(built_zip)

    if len(yaml_conf.during_build):
        with console.status("[bold green]Copying...") as _:
            inter_dir: Path = build_dir / Path("inter")
            if inter_dir.exists():
                shutil.rmtree(inter_dir)
            shutil.copytree(yaml_conf.addon_folder, inter_dir)

        with console.status("[bold green]Executing Build Actions...") as _:
            if "default" in yaml_conf.during_build:
                for action in yaml_conf.during_build["default"]:
                    execute_action(action, inter_dir)
            else:
                if args.db in yaml_conf.during_build:
                    for action in yaml_conf.during_build[args.db]:
                        execute_action(action, inter_dir)

        with console.status("[bold green]Building...") as _:
            time.sleep(2)
            shutil.make_archive(str(build_dir / yaml_conf.build_name), "zip", inter_dir)
    else:
        with console.status("[bold green]Building...") as _:
            time.sleep(2)
            shutil.make_archive(
                str(build_dir / yaml_conf.build_name), "zip", yaml_conf.addon_folder
            )

    # Install addon
    with console.status("[bold green] Installing...") as _:
        for path in map(Path, yaml_conf.install_versions):
            path = path.expanduser()
            if not path.exists():
                path_exists = False
                for test_path in BLENDER_ADDON_DIR:
                    new_path = Path(test_path.format(str(path))).expanduser()
                    if new_path.exists():
                        path = new_path
                        path_exists = True
                        break
                if not path_exists:
                    console.print(
                        f"Path {str(path)} doesn't exist, skipping...",
                        style="bold yellow",
                    )
                    continue

            edited_path: Path = path / Path(yaml_conf.build_name)
            if not edited_path.exists():
                edited_path.mkdir()
            else:
                shutil.rmtree(edited_path)
            shutil.unpack_archive(built_zip, edited_path)
            time.sleep(2)


if __name__ == "__main__":
    main()
