import pdb
import sys

from lark import Lark, ParseTree

GRAMMAR = r"""
%import common.CNAME
%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.INT
%import common.WS
%ignore WS

################################################################################
# Declarations                                                                 #
################################################################################

?decls                  : decl ( ";" decl )* [ ";" ]                                      -> decls

?decl                   : "type"         CNAME              "=" decl_type_variant_cases   -> decl_type_variant
                        | "type"         CNAME              "=" type                      -> decl_type
                        | "def"  [ rec ] CNAME [ ":" type ] "=" value                     -> def
                        | value

decl_type_variant_cases : decl_type_variant_case+                                         -> decl_type_variant_cases

decl_type_variant_case  : "|" CNAME [ "of" type ]                                         -> decl_type_variant_case

################################################################################
# Value                                                                        #
################################################################################

?value                  : "(" value ( ";" value )+ ")"                                    -> seq
                        | "let" [ rec ] CNAME [ ":" type ] "=" value "in" value           -> let
                        | match

?match                  : "match" match "with" match_cases                                -> match
                        | if

match_cases             : match_case+                                                     -> match_cases

match_case              : "|" CNAME [ "of" CNAME ] "->" match                             -> match_case

?if                     : "if" if "then" if "else" if                                     -> if
                        | fun

?fun                    : "fun" CNAME [ ":" type ] "." fun                                -> fun
                        | app

?app                    : app proj                                                        -> app
                        |     proj

?proj                   : atom "[" INT "]"                                                -> proj
                        | atom

?atom                   : "true"                                                          -> ltrue
                        | "false"                                                         -> lfalse
                        | ESCAPED_STRING                                                  -> lstr
                        | SIGNED_INT                                                      -> lint
                        | CNAME                                                           -> lvariable
                        | "(" value "," value ")"                                         -> ltuple
                        | "(" ")"                                                         -> lunit
                        | "(" value ")"

rec                     : "rec"

################################################################################
# Type                                                                         #
################################################################################

?type                   : type_arrow

?type_arrow             : type_prod "->" type_arrow                                       -> tarrow
                        | type_prod

?type_prod              : type_atom "*" type_atom                                         -> tprod
                        | type_atom

?type_atom              : "bool"                                                          -> tbool
                        | "int"                                                           -> tint
                        | "str"                                                           -> tstr
                        | "unit"                                                          -> tunit
                        | CNAME                                                           -> tvariable
                        | "(" type ")"
"""


def parse_source_text(text: str) -> ParseTree:
    try:
        return Lark(GRAMMAR, start="decls").parse(text)
    except Exception as e:
        print("pluh: error: exception while parsing input: " + str(e))
        sys.exit(1)


if __name__ == "__main__":
    print("Start typing source code (CTRL+D to end):")
    tree = parse_source_text(sys.stdin.read())

    print("Parse tree:")
    print(tree.pretty())

    print("Dropping you into a debugger (`tree` is parse tree).")
    pdb.set_trace()
