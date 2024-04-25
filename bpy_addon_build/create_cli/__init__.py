import argparse

from bpy_addon_build.create_cli.action import create_action
from bpy_addon_build.create_cli.project import create_project


def main() -> None:
    """BabEx entry point

    BabEx (a play on Bab and FedEx) is a tool to manage
    BpyBuild projects. It allows creation of a new project,
    adding actions, etc, handling boilerplate and configuration
    and making everything easier in general.
    """

    parser = argparse.ArgumentParser(
        prog="BabEx", description="Manage a BpyBuild project"
    )
    subparsers = parser.add_subparsers(help="sub-command help", dest="command")

    _ = subparsers.add_parser("init", help="Initialize a project")

    parser_action = subparsers.add_parser("action", help="Manage actions in a project")
    action_subparser = parser_action.add_subparsers(
        help="sub-command help", dest="subcommand"
    )
    _ = action_subparser.add_parser("add", help="Add an action to a project")

    args = parser.parse_args()

    if hasattr(args, "command"):
        if args.command == "init":  # type: ignore
            create_project()
        elif args.command == "action":  # type: ignore
            if hasattr(args, "subcommand"):
                if args.subcommand == "add":  # type: ignore
                    create_action()
                else:
                    parser.print_help()


if __name__ == "__main__":
    main()
