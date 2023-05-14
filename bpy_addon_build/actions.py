from typing import Dict, List
from pathlib import Path
import shutil


# Execute an action
def execute_action(action: Dict[str, str], inter_dir: Path):
    # Create a blank file
    if "create_file" in action:
        file_path = inter_dir / Path(action["create_file"])
        with open(file_path, "w") as f:
            f.write("")

    if "copy_file" in action:
        files: List[str] = action["copy_file"].split("->")
        src: Path = Path(files[0]).expanduser()
        dst: Path = inter_dir / Path(files[1])
        shutil.copy2(src, dst)
