import logging

from lark.visitors import Interpreter

from .repl import repl
from .syntax import N
from .syntax import pipeline as prev_pipeline
from .unique import generate_unique_name

_logger = logging.getLogger(__name__)


class AlphaRenamingInterpreter(Interpreter):
    def __init__(
        self,
        venv: dict[str, str] | None = None,
        tenv: dict[str, str] | None = None,
    ) -> None:
        self.venv = venv if venv is not None else dict()
        self.tenv = tenv if tenv is not None else dict()

    def decl_variant(self, t: N) -> None:
        old_name = t.children[0]
        new_name = generate_unique_name(old_name)

        ## Update node in-place.
        t.children[0] = new_name

        ## Update mapping (use parent).
        self.tenv[old_name] = new_name

        self.visit(t.children[1])

    def let(self, t: N) -> None:
        old_name = t.children[0]
        new_name = generate_unique_name(old_name)

        ## Update node in-place.
        t.children[0] = new_name

        ## Update mapping (create new).
        body_mapping = self.venv | {old_name: new_name}

        self.visit(t.children[1])
        AlphaRenamingInterpreter(body_mapping, self.tenv).visit(t.children[2])

    def fun(self, t: N) -> None:
        old_name = t.children[0]
        new_name = generate_unique_name(old_name)

        ## Update node in-place.
        t.children[0] = new_name

        ## Update mapping (create new).
        body_mapping = self.venv | {old_name: new_name}

        AlphaRenamingInterpreter(body_mapping, self.tenv).visit(t.children[1])

    def var(self, t: N) -> None:
        if t.children[0] in self.venv:
            ## Update node in-place.
            t.children[0] = self.venv[t.children[0]]
        # else:
        #     _logger.warning(f"variable is unbound: {t.children[0]}")

    def match_case(self, t: N) -> None:
        constructor_name = t.children[0]
        bind_name = t.children[1]

        if constructor_name in self.venv:
            ## Update node in-place.
            t.children[0] = self.venv[t.children[0]]
        # else:
        #     _logger.warning(f"variable is unbound: {constructor_name}")

        body_mapping = self.venv

        if bind_name is not None:
            old_name = bind_name
            new_name = generate_unique_name(old_name)

            ## Update node in-place.
            t.children[1] = new_name

            ## Update mapping (create new).
            body_mapping = body_mapping | {old_name: new_name}

        AlphaRenamingInterpreter(body_mapping, self.tenv).visit(t.children[2])

    def decl_variant_case(self, t: N) -> None:
        old_name = t.children[0]
        new_name = generate_unique_name(old_name)

        ## Update node in-place.
        t.children[0] = new_name

        ## Update mapping (use parent).
        self.venv[old_name] = new_name

        if t.children[1] is not None:
            self.visit(t.children[1])

    def type_var(self, t: N) -> None:
        if t.children[0] in self.tenv:
            ## Update node in-place.
            t.children[0] = self.tenv[t.children[0]]
        # else:
        #     _logger.warning(f"type variable is unbound: {t.children[0]}")


def pipeline(text: str) -> N:
    _logger.info("Alpha-normalizing tree")
    tree = prev_pipeline(text)
    AlphaRenamingInterpreter().visit(tree)
    return tree


if __name__ == "__main__":

    def callback(line: str) -> None:
        print(pipeline(line).pretty())

    repl(">>> ", callback)
