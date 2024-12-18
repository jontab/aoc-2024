import sys
from pprint import pprint

from lark import Tree

TINT = Tree("tint", [])
TBOO = Tree("tbool", [])

_standard_library = {
    "add": Tree("tarrow", [TINT, Tree("tarrow", [TINT, TINT])]),
    "sub": Tree("tarrow", [TINT, Tree("tarrow", [TINT, TINT])]),
    "mul": Tree("tarrow", [TINT, Tree("tarrow", [TINT, TINT])]),
    "div": Tree("tarrow", [TINT, Tree("tarrow", [TINT, TINT])]),
    "iszero": Tree("tarrow", [TINT, TBOO]),
}

################################################################################
# Alpha-renaming                                                               #
################################################################################

_seen = set()


def generate_unique_name(want: str) -> str:
    result = want
    suffix = 1
    while result in _seen:
        result = f"{want}_{suffix}"
        suffix += 1

    _seen.add(result)
    return result


def alpha_rename(
    node: Tree | None,
    vmap: dict[str, object] | None = None,
    tmap: dict[str, object] | None = None,
) -> tuple[Tree]:
    if not node:
        return None
    vmap = dict() if vmap is None else vmap
    tmap = dict() if tmap is None else tmap
    match node.data:
        case "decl_type_variant":
            # Apply in-place.
            old_name = node.children[0].value
            new_name = generate_unique_name(old_name)
            node.children[0] = new_name

            # TODO: Move tmap[old_name] = new_name line back up here to re-enable recursive types. There's currently a
            #       problem in type-inference with recursive types enabled that allows the recursive type variable to be
            #       unified with an unrelated type.
            case_body_vmap = vmap.copy()
            case_body_tmap = tmap.copy()
            tmap[old_name] = new_name  # Propagate to parent.

            for case in node.children[1].children:
                assert isinstance(case, Tree)
                assert case.data == "decl_type_variant_case"

                # Apply in-place.
                old_case_name = case.children[0].value
                new_case_name = generate_unique_name(old_case_name)
                case.children[0] = new_case_name

                vmap[old_case_name] = new_case_name  # Propagate to parent.

                alpha_rename(case.children[1], case_body_vmap, case_body_tmap)

        case "decl_type":
            old_name = node.children[0].value
            new_name = generate_unique_name(old_name)

            body_tmap = tmap.copy()  # We do not allow recursive non-variant types.

            print(old_name, new_name, body_tmap)
            tmap[old_name] = new_name

            # Apply in-place.
            node.children[0] = new_name
            alpha_rename(node.children[1], vmap, body_tmap)

        case "def":
            is_recursive = node.children[0] is not None
            old_name = node.children[1].value
            new_name = generate_unique_name(old_name)

            val_vmap = vmap.copy()
            if is_recursive:
                val_vmap[old_name] = new_name

            vmap[old_name] = new_name  # Propagate to parent.

            # Apply in-place.
            node.children[1] = new_name
            alpha_rename(node.children[2], None, tmap)
            alpha_rename(node.children[3], val_vmap, tmap)

        ########################################################################
        # Values                                                               #
        ########################################################################

        case "let":
            is_recursive = node.children[0] is not None
            old_name = node.children[1].value
            new_name = generate_unique_name(old_name)

            bod_vmap = vmap.copy() | {old_name: new_name}
            val_vmap = vmap.copy()
            if is_recursive:
                val_vmap[old_name] = new_name

            # Apply in-place.
            node.children[1] = new_name
            alpha_rename(node.children[2], None, tmap)
            alpha_rename(node.children[3], val_vmap, tmap)
            alpha_rename(node.children[4], bod_vmap, tmap)

        case "match":
            alpha_rename(node.children[0], vmap, tmap)
            for case in node.children[1].children:
                assert isinstance(case, Tree)
                assert case.data == "match_case"

                name_constructor = case.children[0].value
                name_bind = case.children[1].value if case.children[1] else None
                body = case.children[2]

                # Apply in-place.
                if name_constructor not in vmap:
                    print("pluh: error: unbound constructor: " + str(name_constructor))
                    sys.exit(1)
                case.children[0] = vmap[name_constructor]

                old_name_bind = name_bind
                new_name_bind = generate_unique_name(old_name_bind)
                case.children[1] = new_name_bind

                alpha_rename(body, vmap | {old_name_bind: new_name_bind}, tmap)

        case "fun":
            # Apply in-place.
            old_name = node.children[0].value
            new_name = generate_unique_name(old_name)
            node.children[0] = new_name

            alpha_rename(node.children[1], None, tmap)
            alpha_rename(node.children[2], vmap | {old_name: new_name}, tmap)

        ########################################################################
        # Variables                                                            #
        ########################################################################

        case "lvariable":
            name = node.children[0].value
            if name not in vmap:
                if name not in _standard_library:
                    print("pluh: error: variable is unbound: " + str(name))
                    sys.exit(1)
                else:
                    return
            node.children[0] = vmap[name]

        case "tvariable":
            name = node.children[0].value
            if name not in tmap:
                print("pluh: error: type variable is unbound: " + str(name))
                sys.exit(1)
            node.children[0] = tmap[name]

        case _:
            for kid in filter(lambda x: isinstance(x, Tree), node.children):
                alpha_rename(kid, vmap, tmap)


################################################################################
# Hindley-Milner type inference                                                #
################################################################################


_hm_venv: dict[str, object] = _standard_library.copy()
_hm_tenv: dict[str, object] = dict()
_hm_subs: dict[str, object] = dict()


def infer_type(t: Tree | None) -> Tree | None:
    if not t:
        return None
    match t.data:
        case "decls":
            return [infer_type(x) for x in t.children][-1]

        case "decl_type_variant":
            variant, cases = t.children[0], t.children[1].children
            variant_type = make_type_variable()

            # 1. If any annotations in the future want to refer to this type by
            #    name, this will allow that.
            _hm_tenv[variant] = variant_type

            for case in cases:
                cons_name = case.children[0]
                cons_args = infer_type(case.children[1])

                # 2. If this constructor takes arguments, the type of the
                #    constructor will be a function. It produces the type
                #    variable of the variant as a result.
                if cons_args:
                    _hm_venv[cons_name] = Tree("tarrow", [cons_args, variant_type])
                else:
                    # 3. If it does not take arguments, then the constructor is
                    #    actually an inhabitant of the type itself.
                    _hm_venv[cons_name] = variant_type
            return make_type("tunit")

        case "decl_type":
            # TODO: Do I need to introduce type-variables and also unify stuff?
            _hm_tenv[t.children[0]] = infer_type(t.children[1])
            return make_type("tunit")

        case "def":
            name, annotate, value = t.children[1:]

            ann_type = infer_type(annotate)
            nam_type = ann_type if ann_type is not None else make_type_variable()

            # 1. See "let" for an explanation.
            _hm_venv[name] = nam_type
            unify(nam_type, infer_type(value))
            return make_type("tunit")

        case "seq":
            return [infer_type(x) for x in t.children][-1]

        case "let":
            name, annotate, value, body = t.children[1:]

            ann_type = infer_type(annotate)
            nam_type = ann_type if ann_type is not None else make_type_variable()

            # 1. We already handled recursion in the alpha-renaming step. If a
            #    variable has the same name, it's guaranteed to be referring to
            #    the same thing. Ergo, we bind the argument before we descend
            #    into the value.
            _hm_venv[name] = nam_type
            unify(nam_type, infer_type(value))

            return infer_type(body)

        case "match":
            value = t.children[0]
            cases = t.children[1].children

            value_type = infer_type(value)
            resul_type = make_type_variable()

            for case in cases:
                cons_name, bind_name, body = case.children

                # 1. We lookup the constructor in the environment to get it's
                #    type and what type variable it produces.
                if cons_name not in _hm_venv:
                    print(f"pluh: error: unbound constructor: {cons_name}")
                    sys.exit(1)
                cons_type = _hm_venv[cons_name]

                # 2. If we are binding a variable, we ensure that that
                #    constructor takes a parameter in the first place via
                #    unification, and we also bind that variable before
                #    descending into the case body.
                if bind_name is not None:
                    bind_type = make_type_variable()
                    unify(Tree("tarrow", [bind_type, value_type]), cons_type)
                    _hm_venv[bind_name] = bind_type

                # 3. We unify the type of the case body with all of the case
                #    bodies before this to ensure all branches return the same
                #    type.
                case_type = infer_type(body)
                unify(resul_type, case_type)

            return resul_type

        case "if":
            cond_type = infer_type(t.children[0])
            iftr_type = infer_type(t.children[1])
            iffa_type = infer_type(t.children[2])
            unify(make_type("tbool"), cond_type)
            unify(iftr_type, iffa_type)
            return iftr_type

        case "fun":
            name, annotate, body = t.children

            # 1. If the user provided an annotation, the argument takes on the
            #    type in that annotation. If they did not, then we set it to a
            #    type variable and evaluate the body with that name in the
            #    environment.
            ann_type = infer_type(annotate)
            arg_type = ann_type if ann_type is not None else make_type_variable()

            _hm_venv[name] = arg_type
            return Tree("tarrow", [arg_type, infer_type(body)])

        case "app":
            fun_type = infer_type(t.children[0])
            arg_type = infer_type(t.children[1])
            res_type = make_type_variable()
            unify(Tree("tarrow", [arg_type, res_type]), fun_type)
            return res_type

        case "proj":
            # 1. This is similar to the application case. We expect the
            #    left-hand side to be of a product-type.
            value_type = infer_type(t.children[0])
            index = int(t.children[1].value)
            should_be = make_product_type(make_type_variable(), make_type_variable())
            unify(should_be, value_type)
            return should_be.children[index]

        ########################################################################
        # Literals                                                             #
        ########################################################################

        case "ltrue" | "lfalse":
            return make_type("tbool")

        case "lstr" | "lint" | "lunit":
            name = "t" + t.data[1:]
            return make_type(name)

        case "lvariable":
            if t.children[0] not in _hm_venv:
                print(f"pluh: error: unbound variable: {t.children[0]}")
                sys.exit(1)
            return _hm_venv[t.children[0]]

        case "ltuple":
            return make_product_type(
                infer_type(t.children[0]),
                infer_type(t.children[1]),
            )

        ########################################################################
        # Types                                                                #
        ########################################################################

        case "tprod":
            return make_product_type(
                infer_type(t.children[0]),
                infer_type(t.children[1]),
            )

        case "tarrow":
            return make_arrow_type(
                infer_type(t.children[0]),
                infer_type(t.children[1]),
            )

        case "tbool" | "tint" | "tstr" | "tunit":
            return make_type(t.data)

        case "tvariable":
            if t.children[0] not in _hm_tenv:
                print(f"pluh: error: undefined type variable: {t.children[0]}")
                sys.exit(1)
            return _hm_tenv[t.children[0]]

        case _:
            raise Exception("unhandled node: " + str(t))


def unify(type1: Tree, type2: Tree) -> None:
    a = resolve(type1)
    b = resolve(type2)
    if a.data == "tvariable":
        if not (b.data == "tvariable" and a.children[0] == b.children[0]):
            if contains(b, a):
                print(f"pluh: error: attempted recursive unification: {a} in {b}")
                sys.exit(1)
            _hm_subs[a.children[0]] = b
        return

    if b.data == "tvariable":
        unify(b, a)
        return

    if a.data == b.data and len(a.children) == len(b.children):
        if a != b:
            for kid1, kid2 in zip(a.children, b.children):
                unify(kid1, kid2)
    else:
        print(f"pluh: error: expected {a.data}, got {b.data}")
        sys.exit(1)


def resolve(t: Tree) -> Tree:
    while t.data == "tvariable" and t.children[0] in _hm_subs:
        t = _hm_subs[t.children[0]]
    return t


def contains(t: Tree, v: Tree) -> bool:
    match t.data:
        case "tarrow" | "tprod":
            return any([contains(x, v) for x in t.children])
        case "tbool" | "tint" | "tstr" | "tunit":
            return False
        case "tvariable":
            return t.children[0] == v.children[0]
        case _:
            raise Exception("unhandled node: " + str(t))


def make_type_variable() -> Tree:
    return Tree("tvariable", [generate_unique_name("T")])


def make_type(name: str) -> Tree:
    return Tree(name, [])


def make_product_type(t1: Tree, t2: Tree) -> Tree:
    return Tree("tprod", [t1, t2])


def make_arrow_type(t1: Tree, t2: Tree) -> Tree:
    return Tree("tarrow", [t1, t2])


def reset_type_environment() -> None:
    global _hm_venv
    _hm_venv = _standard_library.copy()
    _hm_tenv.clear()
    _hm_subs.clear()
