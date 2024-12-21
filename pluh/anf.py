from typing import Callable

from .repl import repl
from .syntax import N
from .type import pipeline as prev_pipeline
from .unique import generate_unique_name


def is_term_atomic(t: N) -> N:
    return t.data in {"false", "true", "int", "var", "unit"}


def normalize_term(t: N) -> N:
    return normalize(t, lambda x: x)


def normalize_name(t: N, cont: Callable[[N], N]) -> N:
    def callback(t2: N) -> N:
        if is_term_atomic(t2):
            return cont(t2)
        else:
            name = generate_unique_name("n")
            return N("let", [name, t2, cont(N("var", [name]))])

    return normalize(t, callback)


def normalize(t: N, cont: Callable[[N], N]) -> N:
    # https://matt.might.net/articles/a-normalization/
    # TODO: Convert this to an Interpreter?
    match t.data:
        ##
        # Declarations
        ##

        case "empty_program" | "decl_variant":
            return t
        case "decls":
            return N(t.data, [normalize_term(x) for x in t.children])

        ##
        # Values
        ##

        case "semi" | "app" | "tup":
            # E.g., complex ";" complex ---> let ... let ... cont(atomic ";" atomic)
            # E.g., complex     complex ---> let ... let ... cont(atomic     atomic)
            # E.g., complex "," complex ---> let ... let ... cont(atomic "," atomic)

            def after_normalize_left(left: N) -> N:
                def after_normalize_right(right: N) -> N:
                    return cont(N(t.data, [left, right]))

                return normalize_name(t.children[1], after_normalize_right)

            return normalize_name(t.children[0], after_normalize_left)

        case "let":
            name, value, body = t.children

            def after_normalize_value(n1: N) -> N:
                return N("let", [name, n1, normalize(body, cont)])

            return normalize(value, after_normalize_value)

        case "match":

            def after_normalize_value(n1: N) -> N:
                cases = []

                for case in t.children[1].children:
                    constructor_name, bind_name, body = case.children
                    kids = [constructor_name, bind_name, normalize_term(body)]
                    cases.append(N("match_case", kids))

                return cont(N("match", [n1, N("match_cases", cases)]))

            return normalize_name(t.children[0], after_normalize_value)

        case "fun":
            return cont(N("fun", [t.children[0], normalize_term(t.children[1])]))

        case "if_expr":

            def after_normalize_condition(n1: N) -> N:
                l = normalize_term(t.children[1])
                r = normalize_term(t.children[2])
                return cont(N("if_expr", [n1, l, r]))

            return normalize_name(t.children[0], after_normalize_condition)

        case "proj_0" | "proj_1":

            def after_normalize_tuple(n1: N) -> N:
                return cont(N(t.data, [n1]))

            return normalize_name(t.children[0], after_normalize_tuple)

        case _:
            if not is_term_atomic(t):
                raise Exception(f"unhandled node: {t.data}")
            return cont(t)


def pipeline(line: str) -> N:
    tree = prev_pipeline(line)
    tree = normalize_term(tree)
    return tree


if __name__ == "__main__":
    repl(">>> ", lambda line: print(pipeline(line).pretty()))
