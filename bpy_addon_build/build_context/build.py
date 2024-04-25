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

import shutil
from pathlib import Path

from bpy_addon_build.build_context import hooks
from bpy_addon_build.build_context.core import BuildContext


def combine_with_build(ctx: BuildContext, path: Path) -> Path:
    """
    Local function to get the path with build name.

    We don't need to have a variable for every single
    path, let's just make a function to handle that.

    ctx: Build context
    path: Path you want to add on to

    Returns:
        New path pointing to path/ctx.build_name
    """
    return path.joinpath(Path(ctx.config.build_name))


def build(ctx: BuildContext) -> Path:
    """
    Function that does the actual building.

    ctx: Build context

    Returns:
        None
    """

    # Create some constants
    BUILD_DIR = ctx.config_path.parent / Path("build")
    STAGE_ONE = BUILD_DIR.joinpath(Path("stage-1"))
    FILTERS = []

    # Get all filters from currently used actions
    if ctx.config.build_actions:
        for name, act in ctx.config.build_actions.items():
            if act.ignore_filters and name in ctx.cli.actions:
                FILTERS += act.ignore_filters

    ADDON_FOLDER = ctx.config_path.parent.joinpath(ctx.config.addon_folder)

    if not BUILD_DIR.exists():
        BUILD_DIR.mkdir()
    if not STAGE_ONE.exists():
        STAGE_ONE.mkdir()
    if STAGE_ONE.exists():
        shutil.rmtree(STAGE_ONE)
        STAGE_ONE.mkdir()

    hooks.run_prebuild_hooks(ctx)
    # For some weird reason, shutil.ignore_patterns
    # expects positional arguments for all patterns,
    # and not a list like most would expect.
    #
    # Sigh...
    #
    # Due to weirdness of the ignore argument, we also
    # need to add an ignore comment for Mypy
    shutil.copytree(
        ADDON_FOLDER,
        combine_with_build(ctx, STAGE_ONE),
        ignore=shutil.ignore_patterns(*FILTERS),  # type: ignore
    )

    hooks.run_main_hooks(ctx, STAGE_ONE, Path(ctx.config.build_name))

    combined_str = str(combine_with_build(ctx, BUILD_DIR))
    shutil.make_archive(combined_str, "zip", STAGE_ONE)
    return Path(combined_str + ".zip")
