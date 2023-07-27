from . import args


def main() -> None:
    cli: args.Args = args.Args()
    cli.parse_args()
    print(cli)


if __name__ == "__main__":
    main()
