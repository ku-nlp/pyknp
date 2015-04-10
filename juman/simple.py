#-*- encoding: utf-8 -*-

from juman import Juman
import unittest

JUMAN = Juman()

def juman(input_str):
    return JUMAN.analysis(input_str)

class SimpleTest(unittest.TestCase):
    def test(self):
        test_str = "この文を解析してください。"
        result = juman(test_str)
        self.assertEqual(len(result.mrph), 7)
        self.assertEqual(''.join(x.midasi for x in result.mrph), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

if __name__ == '__main__':
    unittest.main()
