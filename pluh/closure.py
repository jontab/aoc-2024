from functools import reduce
from pprint import pprint

from .anf import *

################################################################################
# Pre-closure                                                                  #
################################################################################


def simplify_declaration_scopes(t: Tree, last_decl_value: str = "()") -> Tree:
    if len(t.children) == 0:
        return last_decl_value

    assert t.data == "decls"

    first = t.children[0]
    next = Tree("decls", t.children[1:])

    # The only top-level declarations should now be: decl_type_variant, decl_type, and let. The result of the program
    # is the value of the last evaluated expression.
    match first.data:
        case "decl_type_variant":
            scope = simplify_declaration_scopes(next)

            name, cases = t.children
            return Tree("decl_type_variant", [name, cases, scope])
        case "decl_type":
            scope = simplify_declaration_scopes(next)

            name, type = t.children
            return Tree("decl_type", [name, type, scope])
        case "def":
            scope = simplify_declaration_scopes(next)

            name, annotate, value = t.children[1:]
            return Tree("let", [None, name, annotate, value, scope])
        case _:
            name = generate_unique_name("dummy")
            scope = simplify_declaration_scopes(next, Tree("lvariable", [name]))

            return Tree("let", [None, name, None, first, scope])


################################################################################
# Closure                                                                      #
################################################################################


def _combine_free_variables(one: list[str], two: list[str]) -> list[str]:
    return sorted(list(set(one + two)))


def _remove_free_variable(free: list[str], name: str | None) -> None:
    if name and name in free:
        free.remove(name)


def _remove_free_variables(free: list[str], remove: list[str]) -> None:
    for name in remove:
        free.remove(name)


def get_free_variables(t: Tree) -> list[str]:
    # Assume: simplify_declaration_scopes
    # Assume: alpha_rename
    match t.data:
        case "decl_type_variant":
            assert len(t.children) > 2, "Call simplify_declaration_scopes first"
            cases, scope = t.children[1:]
            free = get_free_variables(scope)
            _remove_free_variables(free, get_free_variables(cases))
            return free

        case "decl_type_variant_case":
            return [t.children[0]]

        case "let":
            name, annotate, value, body = t.children[1:]
            free = get_free_variables(body)

            # Note: If "value" contains a reference to "name" itself, assuming
            #       that we already went through the alpha-renaming process,
            #       "let" would be recursive and we would want to remove it from
            #       the free variable list.
            free = _combine_free_variables(free, get_free_variables(value))
            _remove_free_variable(free, name)
            return free

        case "match_case":
            free = get_free_variables(t.children[2])
            _remove_free_variable(free, t.children[1])
            free.append(t.children[0])  # The constructor is always free at this level.
            return free

        case "fun":
            free = get_free_variables(t.children[2])
            _remove_free_variable(free, t.children[0])
            return free

        case "lvariable":
            return [t.children[0]]

        case _:
            result = list()
            for kid in filter(lambda x: isinstance(x, Tree), t.children):
                result = _combine_free_variables(result, get_free_variables(kid))
            return result


def closure(t: Tree | object) -> Tree:
    if isinstance(t, Tree):
        match t.data:
            case "let":
                let_name, let_annotate, let_what, let_body = t.children[1:]
                if let_what.data == "fun":
                    arg_name, arg_annotate, fun_body = let_what.children
                    fun_free = get_free_variables(let_what)
                    let_body = closure(let_body)
                    fun_body = closure(fun_body)
                    return Tree(
                        "function",
                        [
                            let_name,
                            arg_name,
                            fun_free,
                            fun_body,
                            Tree(
                                "let",
                                [
                                    None,
                                    let_name,
                                    None,
                                    Tree(
                                        "closure",
                                        [
                                            let_name,
                                            Tree(
                                                "closurevars",
                                                [
                                                    Tree("lvariable", [varname])
                                                    for varname in fun_free
                                                ],
                                            ),
                                        ],
                                    ),
                                    let_body,
                                ],
                            ),
                        ],
                    )
                else:
                    return Tree(
                        "let",
                        [
                            None,
                            let_name,
                            let_annotate,
                            closure(let_what),
                            closure(let_body),
                        ],
                    )
            case "fun":
                arg_name, arg_type, fun_body = t.children
                name = generate_unique_name("fun")
                return closure(
                    Tree(
                        "let",
                        [
                            None,
                            name,
                            None,
                            Tree("fun", [arg_name, None, fun_body]),
                            Tree("lvariable", [name]),
                        ],
                    )
                )
            case _:
                return Tree(t.data, [closure(c) for c in t.children])
    else:
        return t
