from pathlib import Path
import shutil
from typing import List
from bpy_addon_build.build_context.core import BuildContext, INSTALL_PATHS, console
from bpy_addon_build.build_context import hooks


def get_paths(versions: List[float]) -> List[Path]:
    """Given a list of versions, return paths
    that exist to the corresponding addon folders
    on the system.

    Returns:
        - List[Path]: List of paths that exist
    """
    paths: List[Path] = []
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
