# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
from parse_ebnf import AST, ASTRootNode

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/invalid/*"))

def test_parser_invalid(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    ast = AST()
    with pytest.raises(SyntaxError):
        ast.parse(ebnf.read)
        #In case a syntax error did not occur, print the AST for inspection
        print(str(ast))

    ebnf.close()

