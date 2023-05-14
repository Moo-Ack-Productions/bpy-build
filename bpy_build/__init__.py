import argparse
import os
import shutil
import time
from pathlib import Path
from typing import List
from rich.console import Console
from rich.progress import track

from . import yaml_conf

WORKING_DIR: Path = Path(os.getcwd())
BLENDER_ADDON_DIR: List[str] = ["~/.config/blender/{0}/scripts/addons"]
console = Console()


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Print or check SHA1 (160-bit) checksums.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{parser.prog} version 0.1.0"
    )
    parser.add_argument("files", nargs="*")
    return parser


def parse_file(file: Path) -> yaml_conf.BpyBuildYaml:
    with open(file, "r") as f:
        yaml_config: yaml_conf.BpyBuildYaml = yaml_conf.BpyBuildYaml(f, file)
        return yaml_config


def main():
    parser = init_argparse()
    args = parser.parse_args()
    bpy_build_yaml: Path = WORKING_DIR / Path("bpy-build.yaml")

    if not args.files:
        if bpy_build_yaml.exists():
            print("FOUND c:")
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

    # Create archive and move it to the build directory since shutil makes
    # the archive in the current working directory
    for _ in track(range(2), description="Building..."):
        time.sleep(1)

    shutil.make_archive(
        str(build_dir / yaml_conf.build_name), "zip", yaml_conf.addon_folder
    )

    # Install addon
    for path in track(map(Path, yaml_conf.install_versions), description="Installing..."):
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

        edited_path: Path = (path / Path(yaml_conf.build_name))
        if not edited_path.exists():
            edited_path.mkdir()
        else:
            shutil.rmtree(edited_path)
        shutil.unpack_archive(built_zip, edited_path)
        time.sleep(2)


if __name__ == "__main__":
    main()