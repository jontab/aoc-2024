import unittest

from .anf import normalize
from .closure import *
from .grammar import parse_source_text
from .pre import *


class TestTypeInference(unittest.TestCase):
    def get_type_from_source(self, source: str) -> str:
        tree = parse_source_text(source)
        alpha_rename(tree)
        type = resolve(infer_type(tree))
        return type.data

    def test_decls(self) -> None:
        self.assertEqual("tint", self.get_type_from_source("5"))

    def test_decl_type_variant(self) -> None:
        source = "type UnitOrInt = | Unit | Int of int"
        self.assertEqual("tunit", self.get_type_from_source(source))

    def test_decl_type(self) -> None:
        source = "type IntPair = int * int"
        self.assertEqual("tunit", self.get_type_from_source(source))

    def test_seq(self) -> None:
        source = '(5; "Hello, world!")'
        self.assertEqual("tstr", self.get_type_from_source(source))

    def test_let(self) -> None:
        source = "let x = 5 in x"
        source_rec = "let rec factorial = fun n. (if iszero n then 1 else mul n (factorial (sub n 1))) in factorial 10"
        self.assertEqual("tint", self.get_type_from_source(source))
        self.assertEqual("tint", self.get_type_from_source(source_rec))

    def test_match(self) -> None:
        source = "type NoneOrInt = | None | Int of int; match (Int 5) with | None -> 0 | Int of x -> x"
        self.assertEqual("tint", self.get_type_from_source(source))

    def test_if(self) -> None:
        source = 'if true then "Hello" else "world"'
        self.assertEqual("tstr", self.get_type_from_source(source))

    def test_fun(self) -> None:
        source = 'let alwaysTrue = fun x. true in alwaysTrue "apple"'
        self.assertEqual("tbool", self.get_type_from_source(source))

    def test_app(self) -> None:
        source = "mul 5 5"
        self.assertEqual("tint", self.get_type_from_source(source))

    def test_proj(self) -> None:
        source = "(true, 1)[1]"
        self.assertEqual("tint", self.get_type_from_source(source))


class TestGetFreeVariables(unittest.TestCase):
    def get(self, source: str) -> list[str]:
        tree = parse_source_text(source)
        tree = simplify_declaration_scopes(tree)
        return get_free_variables(tree)

    def test_let(self) -> None:
        source = "let x = 5 in z y x"
        self.assertListEqual(self.get(source), ["y", "z"])

    def test_match_without_type(self) -> None:
        source = "match (Int 5) with | Unit -> x | Int of y -> y"
        self.assertListEqual(self.get(source), ["Int", "Unit", "x"])

    def test_match_with_type(self) -> None:
        source = "type UnitOrInt = | Unit | Int of int; match (Int 5) with | Unit -> x | Int of y -> y"
        self.assertListEqual(self.get(source), [])


if __name__ == "__main__":
    unittest.main()
