import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.prompt import FloatPrompt, Prompt

from bpy_addon_build.config import (
    ADDON_FOLDER,
    BUILD_NAME,
    INSTALL_VERSIONS,
    ConfigDict,
)
from bpy_addon_build.util import EXIT_FAIL, check_string, print_error


def create_project() -> None:
    """Create a new BpyBuild project by asking the user some questions"""

    # Ask user questions related to the project
    #
    # TODO: Create a barebones addon as well that
    # with a "Hello World" panel
    console = Console()
    while True:
        addon_name = Prompt.ask("What is the name of your addon?", default="My Addon")
        if check_string(addon_name):
            break
        print_error("Name uses unsupported characters, please try again", console)

    minimum_supported_version = FloatPrompt.ask(
        "What Blender version do you want to support at the minimum?", default=2.8
    )

    config: ConfigDict = {
        ADDON_FOLDER: "src",
        BUILD_NAME: addon_name,
        INSTALL_VERSIONS: [minimum_supported_version],
    }

    project_root = Path(addon_name)
    src_folder = project_root / Path("src")
    config_file = project_root / Path("bpy-build.yaml")
    init_file = src_folder / Path("__init__.py")
    if project_root.exists():
        print_error("Can't create project directory!", console)
        sys.exit(EXIT_FAIL)

    project_root.mkdir()
    src_folder.mkdir()

    # TODO: Add comments to the outputed
    # config file for the user to better
    # understand
    with open(config_file, "w") as f:
        yaml.dump(config, f)

    # TODO: Add GPL header to the file as well
    with open(init_file, "w") as f:
        _ = f.write("# This project was created with BpyBuild")


if __name__ == "__main__":
    create_project()
