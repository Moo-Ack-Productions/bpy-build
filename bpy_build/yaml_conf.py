from dataclasses import dataclass
from typing import List, TextIO
from pathlib import Path
import yaml


@dataclass
class BpyBuildYaml(object):
    addon_folder: Path
    build_name: str
    install_versions: List[str]

    def __init__(self, file: TextIO, file_path: Path):
        file_data = yaml.safe_load(file)
        self.addon_folder = file_path.parents[0] / Path(file_data["addon_folder"])
        self.build_name = file_data["build_name"]
        self.install_versions = file_data["install_versions"]
