import os


def prebuild() -> None:
    print("HELLO")
    print(os.listdir())


def main() -> None:
    print("DEFAULT")
    print(os.listdir())


if __name__ == "__main__":
    main()
