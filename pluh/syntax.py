import logging
import sys

from lark import Lark, Transformer, Tree

_logger = logging.getLogger(__name__)

GRAMMAR = r"""
%import common.CNAME
%import common.INT
%import common.SIGNED_INT
%import common.WS

COMMENT             : "(*" /.*/ "*)"

%ignore COMMENT
%ignore WS

?start              : decls
                    |                                       -> empty_program

##
# Declarations
##

?decls              : decl ( ";" decl )*                    -> decls
?decl               : decl_variant
                    | value
?decl_variant       : "type" CNAME "=" decl_variant_cases   -> decl_variant

##
# Values
##

?value_parens       : value ";" value_parens                -> semi
                    | value
?value              : "let"    CNAME "=" value "in" value   -> let
                    | "letrec" CNAME "=" value "in" value   -> letrec
                    | match
?match              : "match" match "with" match_cases      -> match
                    | fun
?fun                : "fun" CNAME "->" fun                  -> fun
                    | if
?if                 : "if" if "then" if "else" if           -> if_expr
                    | app
?app                : app proj                              -> app
                    |     proj
?proj               : atom "." "0"                          -> proj_0
                    | atom "." "1"                          -> proj_1
                    | atom
?atom               : "true"                                -> true
                    | "false"                               -> false
                    | SIGNED_INT                            -> int
                    | CNAME                                 -> var
                    | "(" value_parens "," value_parens ")" -> tup
                    | "(" ")"                               -> unit
                    | "(" value_parens ")"

##
# Helpers
##

?match_cases        : match_case+                           -> match_cases
?match_case         : "|" CNAME [ CNAME ] "->" match        -> match_case
?decl_variant_cases : decl_variant_case+                    -> decl_variant_cases
?decl_variant_case  : "|" CNAME [ "of" type ]               -> decl_variant_case

##
# Types
##

?type               : type_fun
?type_fun           : type_tup "->" type_fun                -> type_fun
                    | type_tup
?type_tup           : type_atom "*" type_tup                -> type_tup
                    | type_atom
?type_atom          : "bool"                                -> type_bool
                    | "int"                                 -> type_int
                    | "unit"                                -> type_unit
                    | CNAME                                 -> type_var
                    | "(" type ")"
"""


class N(Tree):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class NTransformer(Transformer):
    def __default__(self, *args, **kwargs) -> N:
        return N(*args, **kwargs)


def _parse_text(text: str) -> Lark:
    try:
        return Lark(GRAMMAR).parse(text)
    except Exception as e:
        print(f"pluh: error: {e}")
        sys.exit(1)


def pipeline(text: str) -> Tree:
    _logger.info("Parsing text")
    tree = _parse_text(text)
    tree = NTransformer().transform(tree)
    return tree
