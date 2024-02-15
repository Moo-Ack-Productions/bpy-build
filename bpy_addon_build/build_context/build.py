from bpy_addon_build.build_context import BuildContext, hooks
import shutil
from pathlib import Path


def build(ctx: BuildContext) -> Path:
    """
    Function that does the actual building.

    Returns:
        None
    """

    # Create some constants
    BUILD_DIR = ctx.config_path.parent / Path("build")
    STAGE_ONE = BUILD_DIR.joinpath(Path("stage-1"))
    FILTERS = []

    # Get all filters from currently used actions
    if ctx.config.build_actions:
        for i in ctx.config.build_actions:
            act = ctx.config.build_actions[i]
            if act.ignore_filters and i in ctx.cli.actions:
                FILTERS += act.ignore_filters

    ADDON_FOLDER = ctx.config_path.parent.joinpath(ctx.config.addon_folder)

    if not BUILD_DIR.exists():
        BUILD_DIR.mkdir()
    if not STAGE_ONE.exists():
        STAGE_ONE.mkdir()
    if STAGE_ONE.exists():
        shutil.rmtree(STAGE_ONE)
        STAGE_ONE.mkdir()

    def combine_with_build(path: Path) -> Path:
        """
        Local function to get the path with build name.

        We don't need to have a variable for every single
        path, let's just make a function to handle that.

        path: Path you want to add on to

        Returns:
            New path pointing to path/ctx.build_name
        """
        return path.joinpath(Path(ctx.config.build_name))

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
        combine_with_build(STAGE_ONE),
        ignore=shutil.ignore_patterns(*FILTERS),  # type: ignore
    )

    hooks.run_main_hooks(ctx, STAGE_ONE, ADDON_FOLDER)
    shutil.make_archive(str(combine_with_build(BUILD_DIR)), "zip", STAGE_ONE)
    return Path(str(combine_with_build(BUILD_DIR)) + ".zip")
