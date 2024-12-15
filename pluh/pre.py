from .node import *


def rewrite_syntactic_sugar(node: Node | object) -> Node:
    """Rewrite expressions such as "let rec" into their syntactic sugar-less equivalents."""
    if not isinstance(node, Node):
        return node

    match node:
        case DeclarationListNode(kids):
            return DeclarationListNode([rewrite_syntactic_sugar(x) for x in kids])

        case VariantTypeDeclarationNode(is_recursive, name, cases):
            return VariantTypeDeclarationNode(
                is_recursive,
                name,
                [rewrite_syntactic_sugar(x) for x in cases],
            )

        case DefinitionNode(is_recursive, name, type, value):
            return DefinitionNode(
                False,
                name,
                type,
                rewrite_syntactic_sugar(FixNode(LambdaNode(name, type, value))),
            )

        ########################################################################
        # Value                                                                #
        ########################################################################

        case LetNode(is_recursive, name, type, value, body):
            return LetNode(
                False,
                name,
                type,
                rewrite_syntactic_sugar(FixNode(LambdaNode(name, type, value))),
                rewrite_syntactic_sugar(body),
            )

        case MatchNode(value, cases):
            return MatchNode(
                rewrite_syntactic_sugar(UnfoldNode(value)),
                [rewrite_syntactic_sugar(x) for x in cases],
            )

        case IfNode(cond, if_true, if_false):
            return IfNode(
                rewrite_syntactic_sugar(cond),
                rewrite_syntactic_sugar(if_true),
                rewrite_syntactic_sugar(if_false),
            )

        case LambdaNode(var_name, var_type, body):
            return LambdaNode(var_name, var_type, rewrite_syntactic_sugar(body))

        case ApplicationNode(fun, arg):
            return ApplicationNode(
                rewrite_syntactic_sugar(fun),
                rewrite_syntactic_sugar(arg),
            )

        case FixNode(body):
            return FixNode(rewrite_syntactic_sugar(body))

        case FoldNode(body):
            return FoldNode(rewrite_syntactic_sugar(body))

        case UnfoldNode(body):
            return UnfoldNode(rewrite_syntactic_sugar(body))

        case IndexNode(value, index):
            return IndexNode(rewrite_syntactic_sugar(value), index)

        case TupleLiteral(kids):
            return TupleLiteral([rewrite_syntactic_sugar(x) for x in kids])

        ########################################################################
        # Type                                                                 #
        ########################################################################

        case ArrowType(left, right):
            return ArrowType(
                rewrite_syntactic_sugar(left),
                rewrite_syntactic_sugar(right),
            )

        case ProductType(kids):
            return ProductType([rewrite_syntactic_sugar(x) for x in kids])

        ########################################################################
        # Literal                                                              #
        ########################################################################

        case _:
            return node
