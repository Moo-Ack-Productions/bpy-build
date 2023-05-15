import subprocess
import shlex
from typing import List
from pathlib import Path
import shutil
import re


# Execute an action
def execute_action(action: str, inter_dir: Path):
    extracted_str = re.search("\((.+?)\)", action)
    if not extracted_str:
        print(
            f"[bold red]Invalid action: {action}, perhaps you forgot parenthesis?[/bold red]"
        )
        quit()

    if "create_file" in action:
        file_path = inter_dir / Path(extracted_str.group(1).replace('"', ""))
        with open(file_path, "w") as f:
            f.write("")

    if "copy_file" in action:
        files: List[str] = extracted_str.group(1).split("->")
        src: Path = Path(files[0].replace('"', "")).expanduser()
        dst: Path = inter_dir / Path(files[1].replace('"', ""))
        shutil.copy2(src, dst)

    if "execute_sh" in action:
        command = shlex.split(extracted_str.group(1))
        subprocess.call(command, shell=True, cwd=inter_dir)
