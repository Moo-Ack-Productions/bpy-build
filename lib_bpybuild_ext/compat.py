from __future__ import annotations

import ast
from pathlib import Path

from typing_extensions import override


class BlInfoVisitor(ast.NodeVisitor):
    """Check for assignment and use of bl_info"""

    def __init__(self) -> None:
        super().__init__()
        self.found_bl_info_set = False
        self.found_bl_info_use = False
        self.line = 0

    @override
    def visit_Name(self, node: ast.Name) -> None:
        if hasattr(node, "id") and hasattr(node, "ctx"):
            var = node.id
            ctx = node.ctx

            # Found an assignment of bl_info
            if var == "bl_info" and isinstance(ctx, ast.Store):  # type: ignore
                self.found_bl_info_set = True
                self.line = node.lineno
            elif var == "bl_info" and isinstance(ctx, ast.Load):  # type: ignore
                self.found_bl_info_use = True
                if self.found_bl_info_set:
                    return
        self.generic_visit(node)


class AbsoluteImportVisitor(ast.NodeVisitor):
    """Check for use of absolute imports"""

    def __init__(self, addon_src: str) -> None:
        super().__init__()
        self.found_absolute_import = False
        self.line = 0
        self.addon_src = addon_src

    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module is not None:
            split_module = node.module.split(".")
            if len(split_module) > 1 and split_module[0] == self.addon_src:
                self.found_absolute_import = True
                self.line = node.lineno
                return
        self.generic_visit(node)


def check_for_compat_issues(
    addon_src: Path, alternate_module_name: str | None = None
) -> None:
    """Detect compatibility issues in addons

    This is based on the migration docs for legacy addons to Extensions,
    as well as findings by developers, Checks for the following:
    - Assigning and using bl_info (note: merely assigning bl_info is fine)
    - Use of absolute imports instead of relative ones

    :param addon_src: The source folder of the addon
    :type addon_src: Path

    :param alternate_module_name: Alternative base module name
    :type alternate_module_name: str | None

    :raises SyntaxError: If any compatibility issues are found
    """

    if not addon_src.is_dir():
        raise NotADirectoryError("addon_src must be a directory!")
    for file in addon_src.rglob("*.py"):
        with open(file, "r") as f:
            root = ast.parse(f.read())
            blinfo_visitor = BlInfoVisitor()
            blinfo_visitor.visit(root)

            if blinfo_visitor.found_bl_info_set and blinfo_visitor.found_bl_info_use:
                error = SyntaxError(
                    "Blender deletes bl_info in extensions! You cannot reference bl_info!"
                )
                error.filename = str(file)
                error.lineno = blinfo_visitor.line

            absolute_import_visitor = AbsoluteImportVisitor(
                str(addon_src)
                if alternate_module_name is None
                else alternate_module_name
            )
            absolute_import_visitor.visit(root)
            if absolute_import_visitor.found_absolute_import:
                error = SyntaxError(
                    "Absolute imports are not allowed for extensions! Please use relative imports."
                )
                error.filename = str(file)
                error.lineno = absolute_import_visitor.line
