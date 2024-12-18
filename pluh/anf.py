import sys
from typing import Callable

from lark import Tree

from .grammar import parse_source_text
from .pre import *

################################################################################
# Normalize                                                                    #
################################################################################


def is_atomic_type(t: Tree) -> bool:
    return t.data in {
        "ltrue",
        "lfalse",
        "lstr",
        "lint",
        "lvariable",
        "lunit",
    }


def normalize_name(t: Tree, fun: Callable[[Tree], Tree]) -> Tree:
    # https://matt.might.net/articles/a-normalization/
    def callback(x: Tree) -> Tree:
        if not is_atomic_type(x):
            name = generate_unique_name("n")
            return Tree("let", [None, name, None, x, fun(Tree("lvariable", [name]))])
        else:
            return fun(x)

    return normalize(t, callback)


def normalize_term(t: Tree) -> Tree:
    identity = lambda x: x
    return normalize(t, identity)



def normalize(t: Tree, fun: Callable[[Tree], Tree] | None = None) -> Tree:
    """Normalizes the tree via using let-statements to simplify and sequence non-atomic expressions.

    Args:
        t: Tree to normalize.
    """
    match t.data:
        case "decls":
            return Tree("decls", [normalize_term(x) for x in t.children])

        case "decl_type_variant":
            return t

        case "def":
            name, annotate, value = t.children[1:]
            return Tree("def", [None, name, annotate, normalize_term(value)])

        case "seq":
            # TODO: Not sure if this is right.
            return fun(Tree("seq", [normalize_term(x) for x in t.children]))

        case "let":
            name, annotate, value, body = t.children[1:]
            return normalize(
                value,
                lambda x: Tree("let", [None, name, annotate, x, normalize(body, fun)]),
            )

        case "match":
            value, cases = t.children[0], t.children[1].children

            def after_normal_match(nvalue: Tree) -> Tree:
                ncases = [
                    Tree(
                        "match_case",
                        [
                            case.children[0],  # Name of constructor.
                            case.children[1],  # Variable to bind to.
                            normalize_term(case.children[2]),  # Normalize the body.
                        ],
                    )
                    for case in cases
                ]
                return Tree("match", [nvalue, Tree("match_cases", ncases)])

            return fun(normalize_name(value, after_normal_match))

        case "if":
            # 1. This is an interesting case. We only want to normalize the condition as if we started pulling out the
            #    code for the true and false branches, then we would be possibly executing code with side-effects for
            #    those branches. We need to maintain this isolation between the branches and the rest of the code.
            cond, iftr, iffa = t.children
            return fun(
                normalize_name(
                    cond,
                    lambda x: Tree(
                        "if", [x, normalize_term(iftr), normalize_term(iffa)]
                    ),
                )
            )

        case "fun":
            name, annotate, body = t.children
            return fun(Tree("fun", [name, annotate, normalize_term(body)]))

        case "app" | "ltuple":
            left, right = t.children
            f = lambda x: normalize_name(right, lambda y: Tree(t.data, [x, y]))
            return fun(normalize_name(left, f))

        case "proj":
            value, index = t.children
            return fun(normalize_name(value, lambda x: Tree("proj", [x, index])))

        case "ltrue" | "lfalse" | "lstr" | "lint" | "lvariable" | "lunit":
            return fun(t)

        case _:
            raise Exception("unhandled node: " + str(t))


def print_as_code(t: Tree, indent: str = "") -> None:
    match t.data:
        case "decls":
            for child in t.children:
                print_as_code(child)
                print(";")

        case "decl_type_variant":
            name, cases = t.children
            print(f"type {name} =")
            print_as_code(cases, indent + "  ")

        case "decl_type_variant_cases":
            for case in t.children:
                name, args = case.children
                print(indent + f"| {name}", end="")

                if args is not None:
                    print(" of ", end="")
                    print_as_code(args)

                print()

        case "def":
            is_recursive, name, annotate_type, value = t.children
            print(indent + "def ", end="")

            if is_recursive is not None:
                print("rec ", end="")

            print(name)

            if annotate_type is not None:
                print(": ", end="")
                print_as_code(annotate_type, "")

            print(" =")
            print_as_code(value, indent + "  ")

        case "seq":
            print_as_code(t.children[0], "")
            print(";")

            for child in t.children[1:]:
                print_as_code(child, indent + "  ")
                print(";")

        case "let":
            is_recursive, name, annotate_type, value, body = t.children
            print(indent + "let ", end="")

            if is_recursive is not None:
                print("rec ", end="")

            print(name, end="")

            if annotate_type is not None:
                print(": ", end="")
                print_as_code(annotate_type, "")

            print(" =")
            print_as_code(value, indent + "  ")
            print()  # Onto the next line, after printing the value.
            print(indent + "in")
            print_as_code(body, indent + "  ")

        case "match":
            value, cases = t.children
            print(indent + "match ", end="")
            print_as_code(value, "")
            print(" with")
            print_as_code(cases, indent + "  ")

        case "match_cases":
            for case in t.children:
                name, variable_name, body = case.children
                print(indent + f"| {name} ", end="")

                if variable_name is not None:
                    print(f"of {variable_name} ", end="")

                print(" -> ", end="")
                print_as_code(body, "")
                print()

        case "if":
            cond, if_true, if_false = t.children
            print(indent + "if ", end="")
            print_as_code(cond, "")
            print(" then ", end="")
            print_as_code(if_true, "")
            print(" else ", end="")
            print_as_code(if_false, "")

        case "fun":
            name, annotate_type, body = t.children
            print(indent + f"fun {name}", end="")

            if annotate_type is not None:
                print(": ", end="")
                print_as_code(annotate_type, "")

            print(". ", end="")
            print_as_code(body, "")

        case "app":
            left, right = t.children
            print(indent + "(", end="")
            print_as_code(left, "")
            print(" ", end="")
            print_as_code(right, "")
            print(")", end="")

        case "ltuple":
            left, right = t.children
            print(indent + "(", end="")
            print_as_code(left, "")
            print(", ", end="")
            print_as_code(right, "")
            print(")", end="")

        case "proj":
            value, index = t.children
            print_as_code(value, indent)
            print(f"[{index}]", end="")

        ########################################################################
        # Literals                                                             #
        ########################################################################

        case "ltrue" | "lfalse":
            print(indent + t.data[1:], end="")

        case "lstr" | "lint" | "lvariable":
            print(indent + t.children[0], end="")

        case "lunit":
            print(indent + "()", end="")

        ########################################################################
        # Types                                                                #
        ########################################################################

        case "tarrow":
            left, right = t.children
            print_as_code(left, indent)
            print(" -> (", end="")
            print_as_code(right, "")
            print(")", end="")

        case "tprod":
            left, right = t.children
            print_as_code(left, indent)
            print(" * ", end="")
            print_as_code(right, "")

        case "tbool" | "tstr" | "tint" | "tunit":
            print(indent + t.data, end="")

        case "tvariable":
            print(indent + t.children[0], end="")

        case _:
            raise Exception("unhandled node: " + str(t))


if __name__ == "__main__":
    print("> ", end="")
    sys.stdout.flush()

    for line in sys.stdin:
        reset_type_environment()
        tree = parse_source_text(line)
        type = resolve(infer_type(tree))
        tree = normalize(tree)

        print("Type:", type.data)
        print(tree.pretty())
        print_as_code(tree)

        print("> ", end="")
        sys.stdout.flush()
