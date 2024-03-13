# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/valid/*"))

def test_example_ast(ebnf_path):
    from parse_ebnf import PT
    from io import StringIO

    pt1 = PT()
    pt2 = PT()

    file = open(ebnf_path, 'r')

    pt1.parse(file.read);
    with StringIO('rule = term | another term;') as f:
        pt2.parse(f.read)

    print(repr(pt1.root.children[0]))

    file.close()

