import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from .alpha import pipeline as alpha_pipeline
from .type import TypeInterpreter, resolve
from .unique import reset_unique_name_generator


@dataclass
class TestCase:
    name: str
    input: str
    output: str


def _get_module_dir() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__)))


def _get_tests_in_folder(folder: str) -> Iterator[TestCase]:
    dir = _get_module_dir().parent / "data" / folder
    inputs = sorted(dir.rglob(r"in*.txt"))
    outputs = sorted(dir.rglob(r"out*.txt"))

    for input, output in zip(inputs, outputs):
        with input.open("r") as input_file, output.open("r") as output_file:
            yield TestCase(
                f"{input.stem} / {output.stem}",
                input_file.read(),
                output_file.read(),
            )


def _run_tests_in_folder(folder: str, callback: Callable[[TestCase], None]) -> int:
    failures = 0
    for case in _get_tests_in_folder(folder):
        print(f"{case.name:40s} ... ", end="")
        sys.stdout.flush()
        try:

            callback(case)
        except Exception as e:
            print(f"FAIL ({e})")
            failures += 1
        else:
            print("OK")
    return failures


def _run_type_tests() -> int:
    def callback(case: TestCase) -> None:
        reset_unique_name_generator()
        interpreter = TypeInterpreter()
        tree = alpha_pipeline(case.input)
        type = resolve(interpreter.visit(tree))
        if str(type) != case.output:
            raise Exception("output does not match")

    print()
    print("Running tests in 'type' folder")
    return _run_tests_in_folder("type", callback)


def run_type_tests() -> None:
    ret = 0
    ret += _run_type_tests()
    sys.exit(ret)


if __name__ == "__main__":
    run_type_tests()
