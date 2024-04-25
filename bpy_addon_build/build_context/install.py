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

from __future__ import annotations

import shutil
from pathlib import Path

from bpy_addon_build.build_context import hooks
from bpy_addon_build.build_context.core import INSTALL_PATHS, BuildContext, console


def get_paths(versions: list[float]) -> list[Path]:
    """Given a list of versions, return paths
    that exist to the corresponding addon folders
    on the system.

    Returns:
        - List[Path]: List of paths that exist
    """
    paths: list[Path] = []
    for v in versions:
        for p in INSTALL_PATHS:
            path = Path(p.format(str(v))).expanduser()
            if not path.exists():
                # For cases like 2.8, 2.9, etc, check with this method
                path = Path(p.format(str(format(v, ".2f")))).expanduser()
                if not path.exists():
                    continue
            paths.append(path)
    return paths


def install(ctx: BuildContext, build_path: Path) -> None:
    """
    Installs the addon to the specified Blender
    versions

    ctx: BuildContext
    build_path: Path to the built addon

    Returns:
        None
    """
    if ctx.config.install_versions is None:
        return
    versions = (
        ctx.cli.versions if len(ctx.cli.versions) else ctx.config.install_versions
    )
    for path in get_paths(versions):
        addon_path = path.joinpath(Path(ctx.config.build_name))
        if not addon_path.exists():
            continue
        shutil.rmtree(addon_path)
        hooks.run_preinstall_hooks(ctx, build_path)
        shutil.unpack_archive(build_path, path)
        if not ctx.cli.supress_messages:
            console.print(f"Installed to {str(path)}", style="green")
        hooks.run_postinstall_hooks(ctx, path)
