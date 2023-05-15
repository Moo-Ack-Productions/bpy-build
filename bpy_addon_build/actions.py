import subprocess
import shlex
from typing import List
from pathlib import Path
import shutil
import re
from rich.console import Console

# Execute an action
def execute_action(action: str, inter_dir: Path, console: Console):
    extracted_str = re.search("\((.+?)\)", action)
    if not extracted_str:
        console.print(
            f"Invalid action: {action}, perhaps you forgot parenthesis?",
            style="[bold red]"
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
        output = subprocess.run(command, shell=True, cwd=inter_dir, capture_output=True)
        if output.stdout != b'':
            console.print(output.stdout)
        if output.stderr != b'':
            console.print(output.stderr)
