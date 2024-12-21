import os
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

from .alpha import pipeline as alpha_pipeline
from .closure import GetFreeVariablesTransformer
from .syntax import pipeline
from .type import TypeInterpreter, resolve
from .unique import reset_unique_name_generator

##
# Unit tests
##


class TestGetFreeVariables(unittest.TestCase):
    def setUp(self) -> None:
        reset_unique_name_generator()

    ##
    # Simple
    ##

    def test_empty_program(self) -> None:
        tree = pipeline("")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, [])

    def test_decl_variant(self) -> None:
        tree = pipeline("type t = | A")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, [])

    def test_decls(self) -> None:
        tree = pipeline("type t = | A; type u = | B")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, [])

        tree = pipeline("apple; pear")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple", "pear"])

    def test_semi(self) -> None:
        tree = pipeline("(apple; pear)")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple", "pear"])

    def test_if_expr(self) -> None:
        tree = pipeline("if orange then orange else apple")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple", "orange"])

    def test_app(self) -> None:
        tree = pipeline("pear orange apple")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple", "orange", "pear"])

    def test_proj(self) -> None:
        tree = pipeline("orange.0")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["orange"])

        tree = pipeline("orange.1")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["orange"])

    ##
    # Complex
    ##

    def test_let(self) -> None:
        tree = pipeline("let apple = orange in apple")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["orange"])

        tree = pipeline("let apple = apple in apple")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple"])

    def test_match(self) -> None:
        tree = pipeline("match myFruit with | apple x -> x | orange y -> z")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["apple", "myFruit", "orange", "z"])

    def test_fun(self) -> None:
        tree = pipeline("fun apple -> orange")
        vars = GetFreeVariablesTransformer().transform(tree)
        self.assertListEqual(vars, ["orange"])

    ##
    # Literals
    ##

    def test_bool(self) -> None:
        vars = GetFreeVariablesTransformer().transform(pipeline("true"))
        self.assertListEqual(vars, [])

        vars = GetFreeVariablesTransformer().transform(pipeline("false"))
        self.assertListEqual(vars, [])

    def test_int(self) -> None:
        vars = GetFreeVariablesTransformer().transform(pipeline("42"))
        self.assertListEqual(vars, [])

    def test_var(self) -> None:
        vars = GetFreeVariablesTransformer().transform(pipeline("apple"))
        self.assertListEqual(vars, ["apple"])

    def test_tup(self) -> None:
        vars = GetFreeVariablesTransformer().transform(pipeline("(apple, orange)"))
        self.assertListEqual(vars, ["apple", "orange"])

    def test_unit(self) -> None:
        vars = GetFreeVariablesTransformer().transform(pipeline("()"))
        self.assertListEqual(vars, [])


##
# File-based tests
##


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
    if ret:
        sys.exit(ret)


if __name__ == "__main__":
    run_type_tests()

    print()
    unittest.main()
