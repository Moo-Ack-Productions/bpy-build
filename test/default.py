import os


def pre_build() -> None:
    print("HELLO")
    print(os.listdir())


def post_install() -> None:
    print("POST INSTALL")
    print(os.listdir())


def main() -> None:
    print("DEFAULT")
    print(os.listdir())


if __name__ == "__main__":
    main()
