import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .alpha import pipeline as prev_pipeline
from .type import TypeInterpreter, resolve
from .unique import reset_unique_name_generator


@dataclass
class TestCase:
    name: str
    input: str
    output: str


def _get_module_dir() -> Path:
    return Path(os.path.dirname(os.path.abspath(__file__)))


def _get_type_tests() -> Iterator[tuple[str, str]]:
    dir = _get_module_dir().parent / "data" / "type"
    inputs = sorted(dir.rglob(r"in*.txt"))
    outputs = sorted(dir.rglob(r"out*.txt"))

    for input, output in zip(inputs, outputs):
        with open(input, "r") as input_file, open(output, "r") as output_file:
            yield TestCase(
                f"{input.stem} / {output.stem}",
                input_file.read(),
                output_file.read(),
            )


def _run_type_test(case: TestCase) -> int:
    print(f"{case.name:40s} ... ", end="")
    sys.stdout.flush()
    try:
        reset_unique_name_generator()
        interpreter = TypeInterpreter()
        tree = prev_pipeline(case.input)
        type = resolve(interpreter.visit(tree))
        if str(type) != case.output:
            raise Exception("output does not match")
    except Exception as e:
        print(f"FAIL ({e})")
        return 1
    else:
        print("OK")
        return 0


def run_type_tests() -> None:
    ret = 0
    for case in _get_type_tests():
        ret += _run_type_test(case)
    sys.exit(ret)


if __name__ == "__main__":
    run_type_tests()
