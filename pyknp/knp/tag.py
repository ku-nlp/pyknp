#-*- encoding: utf-8 -*-

from pyknp import MList
from pyknp import Morpheme
import re
import sys
import unittest

class Tag:
    def __init__(self, spec, id=0):
        self.mrph_list = MList()
        self.parent_id = -1
        self.dpndtype = ''
        self.fstring = ''
        self.id = id
        spec = spec.strip()
        if spec == '+':
            pass
        elif re.match(r'\+ (-?\d+)(\w)(.*)$', spec):
            match = re.match(r'\+ (-?\d+)(\w)(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            sys.stderr.write("Illegal tag spec: %s\n" % spec)
            quit(1)
    def push_mrph(self, mrph):
        self.mrph_list.push_mrph(mrph)
    def spec(self):
        return "+ %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring, self.mrph_list.spec())

class TagTest(unittest.TestCase):
    def test(self):
        tag_str = "+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言><名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        t = Tag(tag_str, 2)
        self.assertEqual(t.id, 2)
        self.assertEqual(t.dpndtype, 'D')
        self.assertEqual(t.parent_id, 1)
        self.assertEqual(len(t.mrph_list), 0)
        m1 = Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>")
        m2 = Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術\" <代表表記:解析/かいせき>")
        t.push_mrph(m1)
        self.assertEqual(len(t.mrph_list), 1)
        t.push_mrph(m2)
        self.assertEqual(len(t.mrph_list), 2)
        self.assertEqual(''.join([m.midasi for m in t.mrph_list]), '構文解析')

if __name__ == '__main__':
    unittest.main()
