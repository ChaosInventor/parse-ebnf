# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_example_ast(ebnf_path):
    from parse_ebnf import AST
    from io import StringIO

    ast1 = AST()
    ast2 = AST()

    file = open(ebnf_path, 'r')

    ast1.parse(file.read);
    with StringIO('rule = term | another term;') as f:
        ast2.parse(f.read)

    print(repr(ast1.root.children[0]))

    file.close()

