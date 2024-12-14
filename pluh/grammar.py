import pdb
import sys

from lark import Lark, ParseTree

GRAMMAR = r"""
%import common.CNAME
%import common.SIGNED_FLOAT
%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.INT
%import common.WS
%ignore WS

################################################################################
# Declarations                                                                 #
################################################################################

decls                   : decl ( ";" decl )* [ ";" ]

?decl                   : "type" [ "rec" ] CNAME              "=" decl_type_variant_cases -> decl_type_variant
                        | "type"           CNAME              "=" type                    -> decl_type
                        | "def"  [ "rec" ] CNAME [ ":" type ] "=" value                   -> def
                        | value

decl_type_variant_cases : decl_type_variant_case+

decl_type_variant_case  : "|" CNAME [ "of" type ]

################################################################################
# Value                                                                        #
################################################################################

?value                  : "let" [ "rec" ] CNAME [ ":" type ] "=" value "in" value         -> let
                        | match

?match                  : "match" match "with" match_cases
                        | if

match_cases             : match_case+

match_case              : "|" CNAME [ "of" CNAME ] "->" match

?if                     : "if" if "then" if "else" if
                        | fun

?fun                    : "fun" CNAME [ ":" type ] "=" fun
                        | app

?app                    : "fix" app                                                       -> fix 
                        | app   proj
                        |       proj

?proj                   : atom "[" INT "]"
                        | atom

?atom                   : "true"                                                          -> lbool
                        | "false"                                                         -> lbool
                        | ESCAPED_STRING                                                  -> lstr
                        | SIGNED_FLOAT                                                    -> lfloat
                        | SIGNED_INT                                                      -> lint
                        | CNAME                                                           -> lvariable
                        | "(" value ( "," value )+ ")"                                    -> lprod
                        | "(" ")"                                                         -> lunit
                        | "(" value ")"

################################################################################
# Type                                                                         #
################################################################################

?type                   : type_arrow

?type_arrow             : type_prod "->" type_arrow
                        | type_prod

?type_prod              : type_atom ( "*" type_atom )*

?type_atom              : "bool"                                                          -> tbool
                        | "int"                                                           -> tint
                        | "float"                                                         -> tfloat
                        | "str"                                                           -> tstr
                        | "(" type ")"
"""


def parse_source_text(text: str) -> ParseTree:
    return Lark(GRAMMAR, start="decls").parse(text)


if __name__ == "__main__":
    print("Start typing source code (CTRL+D to end):")
    tree = parse_source_text(sys.stdin.read())

    print("Parse tree:")
    print(tree.pretty())

    print("Dropping you into a debugger (`tree` is parse tree).")
    pdb.set_trace()
