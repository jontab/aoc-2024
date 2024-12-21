import logging
import sys
from dataclasses import dataclass
from functools import reduce
from pprint import pprint

from lark.visitors import Interpreter

from .alpha import pipeline as alpha_pipeline
from .repl import repl
from .syntax import N
from .unique import generate_unique_name

##
# Hindley-Milner
# Resources:
#   - https://www.cs.cornell.edu/courses/cs4110/2018fa/lectures/lecture27.pdf
#   - https://bernsteinbear.com/blog/type-inference/
#   - https://github.com/rob-smallshire/hindley-milner-python/blob/master/inference.py
#   - https://tracycy.com/projects/hindley-milner-inference
##


@dataclass
class MonoType:
    @property
    def atomic(self) -> bool:
        return True


@dataclass
class TyVar(MonoType):
    name: str
    next: MonoType | None = None

    def __str__(self) -> str:
        if self.next is not None:
            return str(self.next)
        return self.name


@dataclass
class TyCon(MonoType):
    name: str
    args: list[MonoType]

    @property
    def atomic(self) -> bool:
        return self.name not in {"fun", "tup", "sum"}

    def __str__(self) -> str:
        def maybe_wrap_in_parens(x: MonoType) -> str:
            return str(x) if x.atomic else f"({str(x)})"

        match self.name:
            case "bool" | "int" | "unit":
                return self.name
            case "fun":
                return "->".join(map(maybe_wrap_in_parens, self.args))
            case "tup":
                return "*".join(map(maybe_wrap_in_parens, self.args))
            case "sum":
                return "+".join(map(maybe_wrap_in_parens, self.args))
            case _:
                return self.name


@dataclass
class ForAll:
    vars: set[str]
    body: MonoType

    def __str__(self) -> str:
        return f"∀{','.join(self.vars)}. {self.body}"


Bool = TyCon("bool", [])
Int = TyCon("int", [])
Unit = TyCon("unit", [])


def make_fun_type(t1: MonoType, t2: MonoType) -> TyCon:
    return TyCon("fun", [t1, t2])


def make_tup_type(t1: MonoType, t2: MonoType) -> TyCon:
    return TyCon("tup", [t1, t2])


def make_rec_type() -> TyCon:
    return TyCon(generate_unique_name("R"), [])


def make_type_variable() -> TyVar:
    return TyVar(generate_unique_name("T"))


def resolve(t: MonoType) -> MonoType:
    if isinstance(t, TyVar):
        if t.next is not None:
            t.next = resolve(t.next)
            return t.next
    return t


_debug = False
_logger = logging.getLogger(__name__)
standard_library_types = {
    "addi": make_fun_type(Int, make_fun_type(Int, Int)),
    "subi": make_fun_type(Int, make_fun_type(Int, Int)),
    "muli": make_fun_type(Int, make_fun_type(Int, Int)),
    "divi": make_fun_type(Int, make_fun_type(Int, Int)),
    "puti": make_fun_type(Int, Unit),
    "geti": make_fun_type(Unit, Int),
    "iszero": make_fun_type(Int, Bool),
    "gti": make_fun_type(Int, make_fun_type(Int, Bool)),
    "gei": make_fun_type(Int, make_fun_type(Int, Bool)),
    "lti": make_fun_type(Int, make_fun_type(Int, Bool)),
    "lei": make_fun_type(Int, make_fun_type(Int, Bool)),
    "eqi": make_fun_type(Int, make_fun_type(Int, Bool)),
    "nei": make_fun_type(Int, make_fun_type(Int, Bool)),
}

##
# Hindley-Milner type inference
##


def unify(
    t1: MonoType,
    t2: MonoType,
    caller_name: str,
) -> MonoType:
    a = resolve(t1)
    b = resolve(t2)

    if _debug:
        print("Unify")
        print("  Caller name:", caller_name)
        print("  a:          ", str(a))
        print("  b:          ", str(b))

    if isinstance(a, TyVar):
        if not (isinstance(b, TyVar) and a.name == b.name):
            a.next = b
        return

    if isinstance(b, TyVar):
        unify(t2, t1, caller_name)
        return

    assert isinstance(a, TyCon)
    assert isinstance(b, TyCon)
    if a.name != b.name or len(a.args) != len(b.args):
        raise Exception(f"expected {a}, got {b}")

    for k1, k2 in zip(a.args, b.args):
        unify(k1, k2, caller_name)


def generalize(t: MonoType) -> ForAll:
    vars = get_type_variables(t)
    return ForAll(vars, t)


def get_type_variables(t: MonoType) -> set[str]:
    t = resolve(t)
    match t:
        case TyVar():
            return {t.name}
        case TyCon():
            return reduce(lambda x, y: x | get_type_variables(y), t.args, set())


def instantiate(t: ForAll | MonoType) -> MonoType:
    if isinstance(t, ForAll):
        it = t.body
        for var in t.vars:
            it = substitute(var, make_type_variable(), it)
        return it
    return t


def substitute(var: str, replace: MonoType, t: MonoType) -> MonoType:
    match t:
        case TyVar():
            return replace if var == t.name else t
        case TyCon():
            return TyCon(t.name, [substitute(var, replace, x) for x in t.args])


class TypeInterpreter(Interpreter):
    def __init__(
        self,
        venv: dict[str, MonoType | ForAll] | None = None,
        tenv: dict[str, MonoType] | None = None,
    ):
        self.venv = venv if venv is not None else standard_library_types.copy()
        self.tenv = tenv if tenv is not None else dict()

    def empty_program(self, t: N) -> MonoType:
        return Unit

    def decls(self, t: N) -> MonoType:
        return self.visit_children(t)[-1]

    def decl_variant(self, t: N) -> MonoType:
        rec_type = make_rec_type()
        self.tenv[t.children[0]] = rec_type  # E.g., list = R.

        for case in t.children[1].children:
            constructor_name = case.children[0]
            param_type = self.visit(case.children[1]) if case.children[1] else Unit

            # E.g., (int * R) -> R.
            constructor_type = make_fun_type(param_type, rec_type)

            # E.g., Cons = (int * R) -> R.
            self.venv[constructor_name] = constructor_type

        return Unit

    ##
    # Values
    ##

    def semi(self, t: N) -> MonoType:
        return self.visit_children(t)[-1]

    def let(self, t: N) -> MonoType:
        value_type = self.visit(t.children[1])
        self.venv[t.children[0]] = generalize(resolve(value_type))
        return self.visit(t.children[2])

    def letrec(self, t: N) -> MonoType:
        # 1. Fun fact: we don't use generalize here because that would introduce polymorphic recursion. Polymorphic
        #    recursion is not decidable in the general case.
        # 2. For simplicity in compilation, we enforce that the value is a function-type.
        new_type = make_fun_type(make_type_variable(), make_type_variable())
        self.venv[t.children[0]] = new_type
        value_type = self.visit(t.children[1])
        unify(new_type, value_type, "letrec")
        return self.visit(t.children[2])

    def match(self, t: N) -> MonoType:
        value_type = self.visit(t.children[0])
        branch_type = make_type_variable()

        for case in t.children[1].children:
            constructor_name, bind_name, body = case.children

            if constructor_name not in self.venv:
                raise Exception(f"unbound constructor: {constructor_name}")

            constructor_type = self.venv[constructor_name]
            arg_type = make_type_variable()
            rec_type = make_type_variable()
            unify(make_fun_type(arg_type, rec_type), constructor_type, "mat")
            unify(rec_type, value_type, "mat")

            if bind_name is not None:
                self.venv[bind_name] = arg_type

            unify(branch_type, self.visit(body), "mat")

        return branch_type

    def if_expr(self, t: N) -> MonoType:
        unify(Bool, self.visit(t.children[0]), "if_expr")
        branch_type = self.visit(t.children[1])
        unify(branch_type, self.visit(t.children[2]), "if_expr")
        return branch_type

    def fun(self, t: N) -> MonoType:
        self.venv[t.children[0]] = make_type_variable()
        return make_fun_type(self.venv[t.children[0]], self.visit(t.children[1]))

    def app(self, t: N) -> MonoType:
        arg_type = self.visit(t.children[1])
        res_type = make_type_variable()
        unify(
            make_fun_type(arg_type, res_type),
            self.visit(t.children[0]),
            "app",
        )

        return res_type

    def proj_0(self, t: N) -> MonoType:
        value_type = self.visit(t.children[0])
        value_type_want = make_tup_type(make_type_variable(), make_type_variable())
        unify(value_type_want, value_type, "proj_0")
        return value_type_want.args[0]

    def proj_1(self, t: N) -> MonoType:
        value_type = self.visit(t.children[0])
        value_type_want = make_tup_type(make_type_variable(), make_type_variable())
        unify(value_type_want, value_type, "proj_1")
        return value_type_want.args[1]

    def true(self, t: N) -> MonoType:
        return Bool

    def false(self, t: N) -> MonoType:
        return Bool

    def int(self, t: N) -> MonoType:
        return Int

    def var(self, t: N) -> MonoType:
        if t.children[0] not in self.venv:
            raise Exception(f"variable is unbound: {t.children[0]}")
        return instantiate(self.venv[t.children[0]])

    def tup(self, t: N) -> MonoType:
        return make_tup_type(self.visit(t.children[0]), self.visit(t.children[1]))

    def unit(self, t: N) -> MonoType:
        return Unit

    ##
    # Types
    ##

    def type_fun(self, t: N) -> MonoType:
        return make_fun_type(self.visit(t.children[0]), self.visit(t.children[1]))

    def type_tup(self, t: N) -> MonoType:
        return make_tup_type(self.visit(t.children[0]), self.visit(t.children[1]))

    def type_bool(self, t: N) -> MonoType:
        return Bool

    def type_int(self, t: N) -> MonoType:
        return Int

    def type_unit(self, t: N) -> MonoType:
        return Unit

    def type_var(self, t: N) -> TyVar:
        if t.children[0] not in self.tenv:
            raise Exception(f"type variable is unbound: {t.children[0]}")
        return self.tenv[t.children[0]]


def pipeline(text: str) -> N:
    _logger.info("Type-checking program")
    interpreter = TypeInterpreter()
    tree = alpha_pipeline(text)
    try:
        type = resolve(interpreter.visit(tree))
    except Exception as e:
        print(f"pluh: error: {e}")
        sys.exit(1)

    if not isinstance(type, TyCon) or type.name not in ["int", "unit"]:
        msg = f"program must evaluate to int or unit type, got: {type.name}"
        print(msg)
        sys.exit(1)

    return tree


if __name__ == "__main__":

    def callback(line: str) -> None:
        interpreter = TypeInterpreter()
        tree = alpha_pipeline(line)
        type = resolve(interpreter.visit(tree))
        print(type)

        if input("Show environment info? (y/n) ").strip().lower() == "y":
            print("Environment:")
            pprint(interpreter.venv)

            print("Type environment:")
            pprint(interpreter.tenv)

    def intro() -> None:
        print("Type 'p' to show environments and substitution map.")
        print("The following variables are available in your environment.")
        for name, type in standard_library_types.items():
            print(f"{name:8s}: {type}")

    intro()
    repl(">>> ", callback)
