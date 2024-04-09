from bpy_addon_build.api import BabContext


def main(ctx: BabContext) -> None:
    with open((ctx.current_path / "mcprep_dev.txt"), "w") as f:
        f.write("hi guys c:")
