from pathlib import Path
import shutil
from bpy_addon_build.build_context import BuildContext, INSTALL_PATHS, console, hooks


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
    for v in versions:
        installed = False
        for p in INSTALL_PATHS:
            path = Path(p.format(str(v))).expanduser()
            if not path.exists():
                # For cases like 2.8, 2.9, etc, check with this method
                path = Path(p.format(str(format(v, ".2f")))).expanduser()
                if not path.exists():
                    continue
            addon_path = path.joinpath(Path(ctx.config.build_name))
            if addon_path.exists():
                shutil.rmtree(addon_path)
            hooks.run_preinstall_hooks(ctx, build_path)
            shutil.unpack_archive(build_path, path)
            if not ctx.cli.supress_messages:
                console.print(f"Installed to {str(path)}", style="green")
            installed = True
            hooks.run_postinstall_hooks(ctx, path)
        if not installed and not ctx.cli.supress_messages:
            console.print(f"Cound not find {v}", style="yellow")
