import os
from bpy_addon_build.api import BabContext


def clean_up(ctx: BabContext) -> None:
    print("CLEAN UP")
    print(os.listdir())


def pre_build(ctx: BabContext) -> None:
    print("HELLO")
    print(os.listdir())


def post_install(ctx: BabContext) -> None:
    print("POST INSTALL")
    print(os.listdir())


def main(ctx: BabContext) -> None:
    print("DEFAULT")
    print(os.listdir())
