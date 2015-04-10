#-*- encoding: utf-8 -*-

from morpheme import Morpheme
from mlist import MList
from tag import Tag
from tlist import TList
import os
import re
import unittest

class Bunsetsu:
    def __init__(self, spec, id=0):
        self.mrph_list = MList()
        self.tag_list = TList()
        self.parent_id = -1
        self.dpndtype = ''
        self.fstring = ''
        self.id = id
        spec = spec.strip()
        if spec == '*':
            pass
        elif re.match(r'\* (-?\d+)([DPIA])(.*)$', spec):
            match = re.match(r'\* (-?\d+)([DPIA])(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            sys.stderr.write("Illegal bunsetsu spec: %s\n" % spec)
            quit(1)
    def push_mrph(self, mrph):
        if len(self.tag_list) > 0:
            self.tag_list.tag[-1].push_mrph(mrph)
        self.mrph_list.push_mrph(mrph)
    def push_tag(self, tag):
        if len(self.mrph_list) > 0:
            sys.stderr.write("Unsafe addition of tags!\n")
            quit(1)
        self.tag_list.push_tag(tag);
    def spec(self):
        return "* %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring, self.tag_list.spec())

class BunsetsuTest(unittest.TestCase):
    def setUp(self):
        self.bunsetsu_str = "* -1D <BGH:解析/かいせき><文頭><文末><サ変><体言><用言:判><体言止><レベル:C>"
        self.tag1_str = "+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言><名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        self.mrph1_str = "構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>"
        self.tag2_str = "+ -1D <BGH:解析/かいせき><文末><体言><用言:判><体言止><レベル:C>"
        self.mrph2_str = "解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術\" <代表表記:解析/かいせき>"
        self.spec = "%s\n%s\n%s\n%s\n%s\n" % (self.bunsetsu_str, self.tag1_str, self.mrph1_str, self.tag2_str, self.mrph2_str)
    def test_simple(self):
        b = Bunsetsu(self.bunsetsu_str, 3)
        self.assertEqual(b.id, 3)
        self.assertEqual(b.parent_id, -1)
        self.assertEqual(b.dpndtype, "D")
        self.assertEqual(len(b.mrph_list), 0)
        self.assertEqual(len(b.tag_list), 0)
    def test_mrph(self):
        b = Bunsetsu(self.bunsetsu_str)
        m1 = Morpheme(self.mrph1_str)
        b.push_mrph(m1)
        self.assertEqual(len(b.mrph_list), 1)
        m2 = Morpheme(self.mrph2_str)
        b.push_mrph(m2)
        self.assertEqual(len(b.mrph_list), 2)
        self.assertEqual(''.join(x.midasi for x in b.mrph_list), '構文解析')
    def test_spec(self):
        b = Bunsetsu(self.bunsetsu_str)
        t1 = Tag(self.tag1_str)
        m1 = Morpheme(self.mrph1_str)
        t1.push_mrph(m1)
        b.push_tag(t1)
        t2 = Tag(self.tag2_str)
        m2 = Morpheme(self.mrph2_str)
        t2.push_mrph(m2)
        b.push_tag(t2)
        self.assertEqual(b.spec(), self.spec)

if __name__ == '__main__':
    unittest.main()
