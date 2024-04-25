import sys
from pathlib import Path

import yaml
from jinja2 import Template
from rich.console import Console
from rich.prompt import FloatPrompt, Prompt

from bpy_addon_build.config import (
    ADDON_FOLDER,
    BUILD_NAME,
    INSTALL_VERSIONS,
    ConfigDict,
)
from bpy_addon_build.create_cli.util import HELLO_WORLD_TEMPLATE
from bpy_addon_build.util import EXIT_FAIL, check_string, print_error


def create_project() -> None:
    """Create a new BpyBuild project by asking the user some questions"""

    # Ask user questions related to the project
    console = Console()

    # Addon name
    while True:
        addon_name = Prompt.ask("What is the name of your addon?", default="My Addon")
        if check_string(addon_name):
            break
        print_error("Name uses unsupported characters, please try again", console)

    desc = Prompt.ask("What is the description of the addon?", default="Blah blah blah")
    author_name = Prompt.ask("Who are you, the author?", default="Name")
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

    # This generates a file using a Jinja2 template
    #
    # TODO: Allow easy modification of the template, as
    # opposed to storing it only in a variable.
    with open(init_file, "w") as f:
        split_version = str(minimum_supported_version).split(".")
        major_version = split_version[0]
        minor_version = split_version[1]

        if len(minor_version) != 2 and int(major_version) < 3:
            # For inputs such as 2.8, 2.9, etc, but only for pre-3.0
            minor_version += "0"
        del split_version

        bl_info_template = {
            "addon_name": addon_name,
            "author": author_name,
            "major_version": major_version,
            "minor_version": minor_version,
            "desc": desc,
        }

        # Based on the doc string of Template.__new__, this
        # should return a Template, but it's defined as returning
        # Any due to something related to Jinja2's development tools
        template = Template(HELLO_WORLD_TEMPLATE)  # type: ignore
        _ = f.write(template.render(bl_info_template))  # type: ignore


if __name__ == "__main__":
    create_project()
