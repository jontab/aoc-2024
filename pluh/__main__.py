from argparse import ArgumentParser
from typing import TextIO
import sys


from .compile import pipeline


def make_parser() -> ArgumentParser:
    parser = ArgumentParser("pluh", description="A compiler for a functional language.")
    parser.add_argument("file", help="Input file to compile")
    parser.add_argument("-o", "--out", help="Output file", default="a.c")
    return parser


def try_open_file(name: str, mode: str) -> TextIO:
    try:
        return open(name, mode)
    except Exception as e:
        print(f"pluh: error: failed to open file: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = make_parser().parse_args()
    i = try_open_file(args.file, "r")
    o = try_open_file(args.out, "w")
    with i as input_file, o as output_file:
        pipeline(input_file.read(), output_file)


if __name__ == "__main__":
    main()
