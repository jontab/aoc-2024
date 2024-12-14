import argparse
import sys

from .grammar import parse_source_text


def make_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("pluh")
    parser.add_argument("file")
    parser.add_argument("-o", "--out")
    return parser


def get_source_text(source_path: str) -> str:
    try:
        with open(source_path, "r") as file:
            return file.read()
    except Exception as e:
        print("pluh: error: unable to open file for reading: " + str(e))
        sys.exit(1)


def main() -> None:
    args = make_argument_parser().parse_args()
    text = get_source_text(args.file)
    tree = parse_source_text(text)
    print("Tree:", tree)


if __name__ == "__main__":
    main()
