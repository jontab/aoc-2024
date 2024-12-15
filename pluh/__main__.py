import argparse
import sys
from pprint import pprint

from .grammar import parse_source_text
from .node import convert_to_node_tree
from .pre import rewrite_syntactic_sugar


def make_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("pluh")
    parser.add_argument("file")
    parser.add_argument("-o", "--out", default="a.out")
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

    lark_tree = parse_source_text(text)
    tree = convert_to_node_tree(lark_tree)
    tree = rewrite_syntactic_sugar(tree)

    with open(args.out, "w") as file:
        pprint(tree, stream=file)


if __name__ == "__main__":
    main()
