# BSD 3-Clause License
#
# Copyright (c) 2024, Mahid Sheikh
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import string

from rich.console import Console

EXIT_FAIL: int = 1

# Define all allowed characters
# for action names and whatnot
#
# This is restricted to the following:
# - ASCII letters (upper and lower)
# - Numeral digits (0-9)
# - Whitespace
# - Slash (for files)
# - Hyphens and underscores (to prevent issues with importing modules)
ALLOWED_CHARS = set(string.ascii_letters + string.digits + string.whitespace + "-_/")


def check_string(string: str) -> bool:
    """Check if string has proper input.

    This is for security reasons to reduce
    possible security vectors when running
    BpyBuild, by sanitizing input we have
    no control over.

    This isn't the most performant method but
    for our use case it doesn't matter to much.

    Returns:
        - True if the string has only allowed characters
        - False otherwise
    """
    return set(string) <= ALLOWED_CHARS


def print_warning(msg: str, console: Console) -> None:
    """Prints a warning to the console.

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="yellow")


def print_tip(msg: str, console: Console) -> None:
    """Prints a tip to the console.

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="cyan")


def print_error(msg: str, console: Console) -> None:
    """Prints an error to the console.

    msg: string to print
    console: Console from Rich

    Returns:
        None
    """
    console.print(msg, style="red")
