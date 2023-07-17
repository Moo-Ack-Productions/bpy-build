import subprocess
import shlex
from typing import List
from pathlib import Path
import shutil
import re
from rich.console import Console


# Execute an action
def execute_action(action: str, inter_dir: Path, console: Console):
    print(action)
    if isinstance(action, list):
        for cmd in action:
            command = shlex.split(cmd)
            output = subprocess.run(
                command,
                shell=True,
                cwd=inter_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            console.print(output.stdout.decode("UTF-8"))

    elif "create_file" in action:
        extracted_str = re.search(r"\((.+?)\)", action)
        if not extracted_str:
            console.print(
                f"Invalid action: {action}, perhaps you forgot parenthesis?",
                style="bold red",
            )
            quit()

        file_path = inter_dir / Path(extracted_str.group(1).replace('"', ""))
        with open(file_path, "w") as f:
            f.write("")

    elif "copy_file" in action:
        extracted_str = re.search(r"\((.+?)\)", action)
        if not extracted_str:
            console.print(
                f"Invalid action: {action}, perhaps you forgot parenthesis?",
                style="bold red",
            )

        files: List[str] = extracted_str.group(1).split("->")
        src: Path = Path(files[0].replace('"', "")).expanduser()
        dst: Path = inter_dir / Path(files[1].replace('"', ""))
        shutil.copy2(src, dst)

    else:
        console.print(f"Unknown action {action}!", style="bold red")
        quit()
