from dataclasses import dataclass
from typing import Dict, List, Optional, TextIO
from pathlib import Path
import yaml
import rich

@dataclass
class BpyBuildYaml:
    addon_folder: Path
    build_name: str
    install_versions: Optional[List[str]]
    during_build: Optional[Dict[str, List[str]]]

    def __init__(self, file: TextIO, file_path: Path):
        file_data = yaml.safe_load(file)
        if "addon_folder" not in file_data:
            print("[bold red]You need to specify the addon_folder![/bold red]")
            quit()
        if "build_name" not in file_data:
            print("[bold red]You need to specify the build name![/bold red]")
            quit()
            
        self.addon_folder = file_path.parents[0] / Path(file_data["addon_folder"])
        self.build_name = file_data["build_name"]

        if "install_versions" in file_data:
            self.install_versions = file_data["install_versions"]

        if "during_build" in file_data:
            self.during_build = file_data["during_build"]
