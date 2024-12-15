import sys
from dataclasses import dataclass

import lark
from lark import ParseTree


class Node:
    def assert_type(self, arg) -> None:
        """Ensure this object is of the specified type."""
        if type(self) is not arg:
            print(f"pluh: error: expected type {arg}, got: {type(self)}")
            sys.exit(1)


@dataclass
class DeclarationListNode(Node):
    kids: list[Node]


@dataclass
class VariantTypeDeclarationNode(Node):
    @dataclass
    class Case:
        name: str
        of: list[Node]

    is_recursive: bool
    name: str
    cases: list["VariantTypeDeclarationNode.Case"]


@dataclass
class DefinitionNode(Node):
    is_recursive: bool
    name: str
    type: Node | None
    value: Node


################################################################################
# Value                                                                        #
################################################################################


@dataclass
class LetNode(Node):
    is_recursive: bool
    name: str
    type: Node | None
    value: Node
    body: Node


@dataclass
class MatchNode(Node):
    @dataclass
    class Case:
        type_name: str
        bind_name: str | None
        body: Node

    value: Node
    cases: list["MatchNode.Case"]


@dataclass
class IfNode(Node):
    cond: Node
    if_true: Node
    if_false: Node


@dataclass
class LambdaNode(Node):
    var_name: str
    var_type: Node | None
    body: Node


@dataclass
class ApplicationNode(Node):
    fun: Node
    arg: Node


@dataclass
class FixNode(Node):
    body: Node


@dataclass
class FoldNode(Node):
    body: Node


@dataclass
class UnfoldNode(Node):
    body: Node


@dataclass
class IndexNode(Node):
    value: Node
    index: int


@dataclass
class BooleanLiteral(Node):
    value: bool


@dataclass
class StringLiteral(Node):
    value: str


@dataclass
class IntegerLiteral(Node):
    value: str


@dataclass
class VariableLiteral(Node):
    name: str


@dataclass
class TupleLiteral(Node):
    kids: list[Node]


@dataclass
class UnitLiteral(Node):
    pass


################################################################################
# Type                                                                         #
################################################################################


@dataclass
class ArrowType(Node):
    left: Node
    right: Node


@dataclass
class ProductType(Node):
    kids: list[Node]


@dataclass
class BooleanType(Node):
    pass


@dataclass
class IntegerType(Node):
    pass


@dataclass
class StringType(Node):
    pass


@dataclass
class UnitType(Node):
    pass


@dataclass
class VariableType(Node):
    name: str


def convert_to_node_tree(tree: ParseTree) -> Node | None:
    """Convert from Lark parse tree to our custom tree type."""
    if not tree:
        return None

    match tree.data:
        case lark.Token("RULE", "decls"):
            return DeclarationListNode(list(map(convert_to_node_tree, tree.children)))

        case "decl_type_variant":
            return VariantTypeDeclarationNode(
                is_recursive=tree.children[0] is not None,
                name=tree.children[1].value,
                cases=[convert_to_node_tree(x) for x in tree.children[2].children],
            )

        case lark.Token("RULE", "decl_type_variant_case"):
            return VariantTypeDeclarationNode.Case(
                name=tree.children[0].value,
                of=convert_to_node_tree(tree.children[1]),
            )

        case "def":
            return DefinitionNode(
                is_recursive=tree.children[0] is not None,
                name=tree.children[1].value,
                type=convert_to_node_tree(tree.children[2]),
                value=convert_to_node_tree(tree.children[3]),
            )

        ########################################################################
        # Value                                                                #
        ########################################################################

        case "let":
            return LetNode(
                is_recursive=tree.children[0] is not None,
                name=tree.children[1].value,
                type=convert_to_node_tree(tree.children[2]),
                value=convert_to_node_tree(tree.children[3]),
                body=convert_to_node_tree(tree.children[4]),
            )

        case lark.Token("RULE", "match"):
            return MatchNode(
                value=convert_to_node_tree(tree.children[0]),
                cases=[convert_to_node_tree(x) for x in tree.children[1].children],
            )

        case lark.Token("RULE", "match_case"):
            return MatchNode.Case(
                type_name=tree.children[0].value,
                bind_name=tree.children[1].value if tree.children[1] else None,
                body=convert_to_node_tree(tree.children[2]),
            )

        case lark.Token("RULE", "fun"):
            return LambdaNode(
                var_name=tree.children[0].value,
                var_type=convert_to_node_tree(tree.children[1]),
                body=convert_to_node_tree(tree.children[2]),
            )

        case lark.Token("RULE", "app"):
            return ApplicationNode(
                fun=convert_to_node_tree(tree.children[0]),
                arg=convert_to_node_tree(tree.children[1]),
            )

        case lark.Token("RULE", "if"):
            return IfNode(
                cond=convert_to_node_tree(tree.children[0]),
                if_true=convert_to_node_tree(tree.children[1]),
                if_false=convert_to_node_tree(tree.children[2]),
            )

        case lark.Token("RULE", "proj"):
            return IndexNode(
                value=convert_to_node_tree(tree.children[0]),
                index=int(tree.children[1].value),
            )

        case lark.Token("RULE", "type_arrow"):
            return ArrowType(
                left=convert_to_node_tree(tree.children[0]),
                right=convert_to_node_tree(tree.children[1]),
            )

        case lark.Token("RULE", "type_prod"):
            return ProductType(list(map(convert_to_node_tree, tree.children)))

        ########################################################################
        # Literal                                                              #
        ########################################################################

        case "ltrue":
            return BooleanLiteral(value=True)

        case "lfalse":
            return BooleanLiteral(value=False)

        case "lstr":
            return StringLiteral(
                value=tree.children[0].value[1:-1]
            )  # Remove '"' on either side.

        case "lint":
            return IntegerLiteral(value=tree.children[0].value)

        case "lvariable":
            return VariableLiteral(name=tree.children[0].value)

        case "ltuple":
            return TupleLiteral(list(map(convert_to_node_tree, tree.children)))

        case "lunit":
            return UnitLiteral()

        ########################################################################
        # Type                                                                 #
        ########################################################################

        case "tbool":
            return BooleanType()

        case "tint":
            return IntegerType()

        case "tstr":
            return StringType()

        case "tunit":
            return UnitType()

        case "tvariable":
            return VariableType(name=tree.children[0].value)

        case _:
            raise Exception("unhandled type: " + str(tree))
