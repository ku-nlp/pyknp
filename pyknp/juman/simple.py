#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import Juman
import unittest

JUMAN = Juman()


def juman(input_str):
    return JUMAN.analysis(input_str)


class SimpleTest(unittest.TestCase):

    def test(self):
        test_str = u"この文を解析してください。"
        result = juman(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

if __name__ == '__main__':
    unittest.main()
