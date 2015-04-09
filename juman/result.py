#-*- encoding: utf-8 -*-

from mlist import MList
from morpheme import Morpheme

import re
import unittest

def Result(result, pattern=r'^EOS$'):
    result_list = []
    if type(result) != list:
        for line in result.split("\n"):
            result_list.append("%s\n" % line)
    else:
        result_list = result
    mrphs = MList()
    for line in result_list:
        if re.search(pattern, line):
            break
        elif line.startswith("@ @ @"):
            mrphs.push_mrph(Morpheme(line, len(mrphs.mrph)))
        elif line.startswith("@"):
            mrphs.mrph[-1].push_doukei(Morpheme(line, len(mrphs.mrph)))
        else:
            mrphs.push_mrph(Morpheme(line, len(mrphs.mrph)))
    mrphs.set_readonly()
    return mrphs

class ResultTest(unittest.TestCase):
    def setUp(self):
        self.result = "形態素 けいたいそ 形態素 名詞 6 普通名詞 1 * 0 * 0\n" \
                "解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0\n" \
                "の の の 助詞 9 接続助詞 3 * 0 * 0\n" \
                "実行 じっこう 実行 名詞 6 サ変名詞 2 * 0 * 0\n" \
                "例 れい 例 名詞 6 普通名詞 1 * 0 * 0\n" \
                "@ 例 たとえ 例 名詞 6 普通名詞 1 * 0 * 0\n" \
                "@ 例 ためし 例 名詞 6 普通名詞 1 * 0 * 0\n" \
                "EOS"
    def test_midasi(self):
        x = Result(self.result)
        self.assertEqual(len(x.mrph), 5)
        self.assertEqual(''.join(y.midasi for y in x.mrph_list()), "形態素解析の実行例")
    def test_split(self):
        x = Result(["%s\n" % x for x in self.result.split("\n")])
        self.assertEqual(len(x.mrph), 5)
    def test_pattern(self):
        x = Result(self.result, pattern="^EOS$")
        self.assertEqual(len(x.mrph), 5)

if __name__ == '__main__':
    unittest.main()
