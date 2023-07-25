import os
import shutil
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from docopt import docopt

from . import actions
from . import yaml_conf

# Current working directory
WORKING_DIR: Path = Path(os.getcwd())

# All file paths on Windows, MacOS, and Linux based on the Blender Docs
# We use ~ for user directories, and we expand these later on in the code
BLENDER_ADDON_DIR: List[str] = [
    "~/AppData/Roaming/Blender Foundation/Blender/{0}/scripts/addons",
    "~/Library/Application Support/Blender/{0}/scripts/addons",
    "~/.config/blender/{0}/scripts/addons",
]

# Rich console
console = Console()


USAGE = """
Usage:
    bpy-addon-build (-h | --help)
    bpy-addon-build ((-b | --during-build) <action>) [<file>]
    bpy-addon-build [<file>] [((-b | --during-build) <action>)] ((-v | --versions) <versions>...)
    bpy-addon-build [<file>]

Options:
  -h --help     Show this screen.
  -b --during-build      Execute a set of actions in addition to the default action
  -v 
"""


# Parse a file from a Path
def parse_file(file: Path) -> yaml_conf.BpyBuildYaml:
    with open(file, "r") as f:
        yaml_config: yaml_conf.BpyBuildYaml = yaml_conf.BpyBuildYaml(f, file)
        return yaml_config


# Main function
def main():
    args = docopt(USAGE)
    bpy_build_yaml: Path = WORKING_DIR / Path("bpy-build.yaml")

    if not args["<file>"]:
        if bpy_build_yaml.exists():
            pass
        else:
            console.print(
                "Can't find bpy-build.yaml, maybe pass it directly?", style="bold red"
            )
            return
    else:
        bpy_build_yaml = Path(args["<file>"]).resolve()

    yaml_conf = parse_file(bpy_build_yaml)
    build_dir = bpy_build_yaml.parents[0] / Path("build")
    copy_dir = build_dir / Path(yaml_conf.build_name + "subfolder")
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

    # If there are build actions
    if len(yaml_conf.during_build):
        # Copy the folder
        with console.status("[bold green]Copying...") as _:
            inter_dir: Path = build_dir / Path("inter")
            if inter_dir.exists():
                shutil.rmtree(inter_dir)
            shutil.copytree(yaml_conf.addon_folder, inter_dir)

        # Perform actions
        with console.status("[bold green]Executing Build Actions...") as _:
            # Peform default action
            if "default" in yaml_conf.during_build:
                for action in yaml_conf.during_build["default"]:
                    actions.execute_action(action, inter_dir, console)
            # Perform extra action
            if args["--during-build"] and args["<action>"] in yaml_conf.during_build:
                for action in yaml_conf.during_build[args["<action>"]]:
                    actions.execute_action(action, inter_dir, console)
        # Rebuild
        if copy_dir.exists():
            shutil.rmtree(copy_dir)
        copy_dir.mkdir()
        shutil.copytree(inter_dir, copy_dir / Path(yaml_conf.build_name))
        with console.status("[bold green]Building...") as _:
            shutil.make_archive(str(build_dir / yaml_conf.build_name), "zip", copy_dir)
    else:
        # Build addon
        if copy_dir.exists():
            shutil.rmtree(copy_dir)
        copy_dir.mkdir()
        shutil.copytree(yaml_conf.addon_folder, copy_dir / Path(yaml_conf.build_name))
        with console.status("[bold green]Building...") as _:
            shutil.make_archive(str(build_dir / yaml_conf.build_name), "zip", copy_dir)

    # Install addon
    with console.status("[bold green] Installing...") as _:
        versions_list = yaml_conf.install_versions
        if len(args["<versions>"]):
            versions_list = args["<versions>"]
        for path in map(Path, versions_list):
            # Expand the ~ in the path
            path = path.expanduser()
            if not path.exists():
                found: Optional[Path] = next(
                    (
                        Path(test_path.format(str(path))).expanduser()
                        for test_path in BLENDER_ADDON_DIR
                        if Path(test_path.format(str(path))).expanduser().exists()
                    ),
                    None,
                )
                if found:
                    path = found
                else:
                    console.print(
                        f"Path {str(path)} doesn't exist, skipping...",
                        style="bold yellow",
                    )
                    continue
            addon_path: Path = path / Path(yaml_conf.build_name)
            console.print(f"Installing in {str(path)}", style="bold green")
            shutil.rmtree(addon_path, ignore_errors=True)
            shutil.unpack_archive(built_zip, path)
            console.print(f"Installed to {addon_path}")


if __name__ == "__main__":
    main()
