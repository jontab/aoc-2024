from dataclasses import dataclass
from functools import reduce
from pprint import pprint

from lark import Transformer

from .anf import pipeline as prev_pipeline
from .repl import repl
from .syntax import N
from .unique import generate_unique_name

FreeVars = list[str]


##
# GetFreeVariablesTransformer
##


def _combine_free_vars(v1: FreeVars, v2: FreeVars) -> FreeVars:
    return sorted(list(set(v1 + v2)))


def _remove_from_free_vars(var: str, vars: FreeVars) -> FreeVars:
    return [v for v in vars if v != var]


class GetFreeVariablesTransformer(Transformer):
    ##
    # Simple
    ##

    def empty_program(self, _) -> FreeVars:
        return []

    def decl_variant(self, _) -> FreeVars:
        return []

    def decls(self, kids: list[FreeVars]) -> FreeVars:
        return reduce(_combine_free_vars, kids, [])

    def semi(self, kids: list[FreeVars]) -> FreeVars:
        return reduce(_combine_free_vars, kids, [])

    def if_expr(self, kids: list[FreeVars]) -> FreeVars:
        return reduce(_combine_free_vars, kids, [])

    def app(self, kids: list[FreeVars]) -> FreeVars:
        return reduce(_combine_free_vars, kids, [])

    def proj_0(self, kids: list[FreeVars]) -> FreeVars:
        return kids[0]

    def proj_1(self, kids: list[FreeVars]) -> FreeVars:
        return kids[0]

    ##
    # Complex
    ##

    def let(self, kids: list[str | FreeVars]) -> FreeVars:
        name, value_vars, body_vars = kids
        ret = _remove_from_free_vars(str(name), body_vars)
        ret = _combine_free_vars(ret, value_vars)
        return ret

    def letrec(self, kids: list[str | FreeVars]) -> FreeVars:
        name, value_vars, body_vars = kids
        body_vars = _remove_from_free_vars(str(name), body_vars)
        value_vars = _remove_from_free_vars(str(name), value_vars)
        ret = _combine_free_vars(value_vars, body_vars)
        return ret

    def match(self, kids: list[str | N | FreeVars]) -> FreeVars:
        value_vars, cases = kids[0], kids[1].children
        return reduce(_combine_free_vars, cases, value_vars)

    def match_case(self, kids: list[str | FreeVars]) -> FreeVars:
        constructor_name, bind_name, body_vars = kids
        ret = _remove_from_free_vars(str(bind_name), body_vars)
        return ret

    def fun(self, kids: list[str | FreeVars]) -> FreeVars:
        arg_name, body_vars = kids
        return _remove_from_free_vars(str(arg_name), body_vars)

    ##
    # Literals
    ##

    def true(self, _) -> FreeVars:
        return []

    def false(self, _) -> FreeVars:
        return []

    def int(self, _) -> FreeVars:
        return []

    def var(self, kids: list[N]) -> FreeVars:
        return [str(kids[0])]

    def tup(self, kids: list[FreeVars]) -> FreeVars:
        return reduce(_combine_free_vars, kids, [])

    def unit(self, _) -> FreeVars:
        return []

    def closure(self, kids: list[str | FreeVars]) -> FreeVars:
        return kids[1]


##
# ClosureTransformer
##


@dataclass
class ClosedFun:
    name: str
    arg: str
    freevars: FreeVars
    body: N


class VariableToEnvironmentTransformer(Transformer):
    def __init__(self, freevars: list[str]) -> None:
        self.freevars = freevars

    def var(self, kids: list[N]) -> N:
        name = str(kids[0])
        if name in self.freevars:
            ix = self.freevars.index(name)
            return N("env", [ix])
        else:
            return N("var", [name])  # Variable is bound.


class ClosureTransformer(Transformer):
    def __init__(self, funs: list[N]) -> N:
        self.funs = funs

    def fun(self, kids: list[N]) -> N:
        # 1. Generate a new name for the (currently anonymous) function.
        # 2. Gather the free variables in its body.
        # 3. Transform the references to those free variables in the body to indexes into an "environment".
        freevars = GetFreeVariablesTransformer().transform(N("fun", kids))
        function = ClosedFun(
            generate_unique_name("fun"),
            str(kids[0]),
            freevars,
            VariableToEnvironmentTransformer(freevars).transform(kids[1]),
        )
        self.funs.append(function)
        return N("closure", [function.name, freevars])


##
# VariantExtractingTransformer
##


class VariantExtractingTransformer(Transformer):
    def __init__(self, constructors: dict[str, int]) -> None:
        self.constructors = constructors

    def decl_variant(self, kids: list[N]) -> N:
        for i, case in enumerate(kids[1].children):
            constructor_name = str(case.children[0])
            self.constructors[constructor_name] = i
        return N("unit", [])

    def var(self, kids: list[N]) -> N:
        name = str(kids[0])
        if name in self.constructors:
            variant_index = self.constructors[name]
            l = N("closure", ["pluh_rt_make_variant", []])
            r = N("int", [str(variant_index)])
            return N("app", [l, r])
        else:
            return N("var", kids)


@dataclass
class PreCompileInfo:
    constructors: dict[str, int]
    funs: list[ClosedFun]
    tree: N


def pipeline(text: str) -> PreCompileInfo:
    info = PreCompileInfo(dict(), [], None)
    info.tree = prev_pipeline(text)
    info.tree = VariantExtractingTransformer(info.constructors).transform(info.tree)
    info.tree = ClosureTransformer(info.funs).transform(info.tree)
    return info


if __name__ == "__main__":

    def callback(line: str) -> None:
        info = pipeline(line)

        print()
        print("Constructors:")
        pprint(info.constructors)

        print()
        print("Funs:")
        pprint(info.funs)

        print()
        print("Tree:")
        print(info.tree.pretty())

    repl(">>> ", callback)
