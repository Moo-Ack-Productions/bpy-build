# BSD 3-Clause License
#
# Copyright (c) 2025, Maryam Sheikh (Mahid Sheikh)
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

import ast
from pathlib import Path
from typing import Any, Union, cast, no_type_check

from typing_extensions import override

from bpy_addon_build.api import BabContext, BpyError, BpyVariableDef
from lib_bpybuild_ext import BLENDER_MANIFEST, compat, get_manifest_data, verify


class BlInfoVersionExtractVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.version: list[int] = []

    @override
    @no_type_check  # ast module inherently uses Any a lot
    def visit_Assign(self, node: ast.Assign) -> Any:
        targets = node.targets

        if len(targets) > 1 or not len(targets):
            self.generic_visit(node)
            return

        target_name = targets[0]
        if not isinstance(target_name, ast.Name):
            self.generic_visit(node)
            return
        else:
            if target_name.id != "bl_info":
                self.generic_visit(node)
                return

        value = cast(ast.Dict, node.value)
        assert isinstance(value, ast.Dict)

        keys = value.keys
        values = value.values

        for idx, key_node in enumerate(keys):
            if not isinstance(key_node, ast.Constant):
                self.generic_visit(node)
                continue

            if key_node.value != "version":
                continue

            # In CPython's AST, values in dictionaries
            # are at the same index as the key
            value_node = values[idx]
            if not isinstance(value_node, ast.Tuple):
                continue

            # Verify that all values in tuple are constants
            # and that said constants are integers. Also use
            # this time to extract values
            for elt in value_node.elts:
                # At this point, it better be a constant or else
                # we have no hope in parsing this
                if not isinstance(elt, ast.Constant):
                    self.generic_visit(node)
                    return

                # This better be an integer or else there's no good
                # way to convert this to a nice string
                if not isinstance(elt.value, int):
                    self.generic_visit(node)
                    return

                self.version.append(cast(int, elt.value))

            # After all of this, let's break,
            # since there can only be one bl_info
            break
        self.generic_visit(node)


def dynamic_name(ctx: BabContext) -> Union[list[BpyVariableDef], BpyError]:
    if ctx.is_extension:
        manifest_path = Path(ctx.current_path, BLENDER_MANIFEST)
        manifest_data = get_manifest_data(manifest_path)

        # Let's perform verification first, just to make sure the data is correct
        verify.verify_manifest(manifest_data, manifest_path)
        compat.check_for_compat_issues(
            ctx.current_path, ctx.builtin_config.addon_folder
        )

        return [BpyVariableDef("version", manifest_data.version)]
    else:
        init_file = ctx.current_path.joinpath("__init__.py")
        with open(init_file, "r") as f:
            root = ast.parse(f.read())
            visitor = BlInfoVersionExtractVisitor()
            visitor.visit(root)
            if not len(visitor.version):
                return BpyError(f"No version extracted from {str(init_file)}")
            return [
                BpyVariableDef("version", ".".join([str(x) for x in visitor.version]))
            ]
