from bpy_addon_build.api import BabContext


def clean_up(ctx: BabContext) -> None:
    print("CLEAN UP", ctx.current_path)


def pre_build(ctx: BabContext) -> None:
    print("PRE BUILD", ctx.current_path)


def post_install(ctx: BabContext) -> None:
    print("POST INSTALL", ctx.current_path)


def main(ctx: BabContext) -> None:
    print("MAIN", ctx.current_path)
