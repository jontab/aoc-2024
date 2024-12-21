from typing import Callable, TextIO

from .closure import ClosedFun, PreCompileInfo
from .closure import pipeline as prev_pipeline
from .syntax import N
from .unique import generate_unique_name

ObjType = "pluh_obj_t"
EnvType = "pluh_env_t"

_file: TextIO = None
_info: PreCompileInfo = None

_preamble = f"""
#include "pluh.h"
"""


def _write(text: str, end="\n") -> None:
    assert _file, "file must be set before attempting to compile"
    print(text, file=_file, end=end)


def _set_compile_context(file: TextIO, info: PreCompileInfo):
    global _file, _info
    _file = file
    _info = info


def _make_unit_object() -> str:
    return f"({ObjType})(0)"


def _ignore_result(result: str) -> None:
    _write(f"    (void)({result});")


##
# Compilation methods
##


def _compile_decls(t: N, then: Callable[[str], None]) -> None:
    for decl in t.children[:-1]:
        _compile_node(decl, _ignore_result)
    _compile_node(t.children[-1], then)


def _compile_letrec(t: N, then: Callable[[str], None]) -> None:
    # Note: The value must be a closure because we enforced it in an earlier stage.
    let_name, let_value, let_body = t.children
    assert let_value.data == "closure"

    # 1. First, let's create the closure. If the closure, in fact, wants a reference to itself, it needs to wait until
    #    after the closure is created.
    _write(f"    {ObjType} {let_name} = ", end="")

    function_name, freevars = let_value.children
    _write(f"pluh_closure_create(({ObjType})({function_name})", end="")
    _write(f", {len(freevars)}", end="")
    arg_names = ["NULL" if x == let_name else x for x in freevars]
    if arg_names:
        _write(f", {', '.join(arg_names)}", end="")
    _write(f");")

    # 2. Now, if the closure wants a reference to itself, we can inject it into the environment.
    if let_name in freevars:
        let_name_ix = freevars.index(let_name)
        _write(f"    ((pluh_closure_t *)({let_name}))", end="")
        _write(f"->e.data[{let_name_ix}] = {let_name};")

    # 3. Next, we compile the body as normal.
    _compile_node(let_body, then)


def _compile_closure(t: N, then: Callable[[str], None]) -> None:
    function_name, freevars = t.children
    name = generate_unique_name("closure")

    _write(f"")
    _write(f"    {ObjType} {name} = ", end="")

    _write(f"pluh_closure_create(({ObjType})({function_name})", end="")
    _write(f", {len(freevars)}", end="")
    if freevars:
        _write(f", {', '.join(freevars)}")
    _write(f");")

    then(name)


def _compile_if_expr(t: N, then: Callable[[str], None]) -> None:
    con, tru, fls = t.children
    resname = generate_unique_name("if_result")
    aftname = resname + "_after"
    truname = resname + "_true"
    _write(f"    {ObjType} {resname};")

    def set_if_result(value: str) -> None:
        _write(f"    {resname} = {value};")

    # 1. Condition.
    _write(f"    if (", end="")
    _compile_node(con, lambda x: _write(x, end=""))
    _write(f")")
    _write(f"        goto {truname};")

    # 2. False.
    _compile_node(fls, set_if_result)
    _write(f"    goto {aftname};")

    # 3. True.
    _write(f"{truname}:")
    _compile_node(tru, set_if_result)

    # 4. After.
    _write(f"{aftname}:")
    then(resname)


def _compile_match(t: N, then: Callable[[str], None]) -> None:
    value = t.children[0]
    cases = t.children[1].children

    value_name = generate_unique_name("match_value")
    _write(f"    {ObjType} {value_name};")
    _compile_node(value, lambda x: _write(f"    {value_name} = {x};"))

    _write(f"    switch (((pluh_variant_t *)({value_name}))->type)")
    _write(f"    {{")
    for case in cases:
        constructor_name, arg_name, body = case.children
        constructor_ix = _info.constructors[constructor_name]
        _write(f"    case {constructor_ix}:")
        _write(f"        goto {value_name}_{constructor_name};")
    _write(f"    default:")
    _write(f"        abort();")
    _write(f"    }}")
    _write(f"")

    result_name = generate_unique_name("match_result")
    _write(f"    {ObjType} {result_name};")

    for case in cases:
        constructor_name, arg_name, body = case.children
        _write(f"{value_name}_{constructor_name}:")
        if arg_name is not None:
            _write(f"    {ObjType} {arg_name} = ", end="")
            _write(f"((pluh_variant_t *)({value_name}))->data;")

        def case_body_then(v: str) -> None:
            _write(f"    {result_name} = {v};")
            _write(f"    goto {value_name}_after;")

        _compile_node(body, case_body_then)

    _write(f"{value_name}_after:")
    then(result_name)


def _compile_node(t: N, return_node_result: Callable[[str], None]) -> None:
    match t.data:
        case "empty_program":
            return_node_result(_make_unit_object())

        ##
        # Declarations
        ##

        case "decls":
            _compile_decls(t, return_node_result)

        ##
        # Values
        ##

        case "semi":
            _compile_node(t.children[0], _ignore_result)
            _compile_node(t.children[1], return_node_result)

        case "letrec":
            _compile_letrec(t, return_node_result)

        case "let":
            name, value, body = t.children
            _compile_node(value, lambda x: _write(f"    {ObjType} {name} = {x};"))
            _compile_node(body, return_node_result)

        case "closure":
            _compile_closure(t, return_node_result)

        case "match":
            _compile_match(t, return_node_result)

        case "if_expr":
            _compile_if_expr(t, return_node_result)

        case "app":
            l, r = t.children

            def lthen(lval: str) -> None:
                def rthen(rval: str) -> None:
                    return_node_result(f"call({lval}, {rval})")

                _compile_node(r, rthen)

            _compile_node(l, lthen)

        case "proj_0" | "proj_1":
            value = t.children[0]

            def got_value_result(v: str) -> None:
                field = "0" if t.data == "proj_0" else "1"
                return_node_result(f"(((pluh_tup_t *)({v}))->data[{field}])")

            _compile_node(value, got_value_result)

        ##
        # Literals
        ##

        case "true":
            return_node_result(f"({ObjType})(1)")

        case "false":
            return_node_result(f"({ObjType})(0)")

        case "int":
            return_node_result(f"({ObjType})(intptr_t)({t.children[0]})")

        case "var":
            return_node_result(t.children[0])

        case "env":
            ix = t.children[0]
            return_node_result(f"e->data[{ix}]")

        case "tup":
            args = []
            _compile_node(t.children[0], lambda l: args.append(l))
            _compile_node(t.children[1], lambda r: args.append(r))
            value = f"pluh_tup_create(2, {', '.join(args)})"
            return_node_result(value)

        case "unit":
            return_node_result(_make_unit_object())

        case _:
            assert False, f"unhandled node: {t.data}"


def _compile_function(fun: ClosedFun) -> None:
    _write(f"{ObjType} {fun.name}({ObjType} {fun.arg}, {EnvType} *e)")
    _write(f"{{")

    def then(result: str) -> None:
        _write(f"    return {result};")

    _compile_node(fun.body, then)
    _write(f"}}\n")


def _compile_functions() -> None:
    for fun in _info.funs:
        _compile_function(fun)


def pipeline(text: str, file: TextIO) -> None:
    _set_compile_context(file, prev_pipeline(text))
    _write(_preamble)
    _compile_functions()

    def then(v: str) -> None:
        _write(f"    return (int)(intptr_t)({v});")

    _write(f"int main(void)")
    _write(f"{{")
    _write(f"    pluh_init();")
    _compile_node(_info.tree, then)
    _write(f"}}")
