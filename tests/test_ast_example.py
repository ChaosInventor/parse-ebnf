# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import glob

import pytest

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_example_ast(ebnf_path):
    from io import StringIO

    from parse_ebnf import PT, parsing

    pt1 = PT()
    pt2 = PT()

    file = open(ebnf_path)

    pt1 = parsing.parse_pt(file.read)
    with StringIO('rule = term | another term;') as f:
        pt2 = parsing.parse_pt(f.read)

    print(repr(pt1.root.children[0]))

    file.close()

