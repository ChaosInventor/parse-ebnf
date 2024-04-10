# SPDX-FileCopyrightText: 2023-present ChaosInventor <chaosinventor@yandex.com>
#
# SPDX-License-Identifier: MIT

import pytest
import glob
from parse_ebnf import PT, parsing, EBNFError
from parse_ebnf.nodes import Root

pytestmark = pytest.mark.parametrize("ebnf_path", glob.glob("tests/resources/invalid/*"))

def test_parser_invalid(ebnf_path):
    ebnf = open(ebnf_path, 'r')

    pt = PT()
    with pytest.raises(EBNFError):
        pt = parsing.parsePT(ebnf.read)
        #In case a syntax error did not occur, print the PT for inspection
        print(str(pt))

    ebnf.close()

