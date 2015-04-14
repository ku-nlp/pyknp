#-*- encoding: utf-8 -*-

from pyknp import MList
from pyknp import Morpheme
from pyknp import Tag
import sys
import unittest

class TList:
    def __init__(self): 
        self._tag = []
        self._TLIST_READONLY = False
        self._TLIST_NODESTROY = False
    def push_tag(self, tag):
        if not self._TLIST_READONLY:
            self._tag.append(tag)
    def push_mrph(self, mrph):
        if len(self._tag) > 0:
            self._tag[-1].push_mrph(mrph)
        else:
            sys.stderr.write("Cannot push mrph: no tags.")
            quit(1)
    def spec(self):
        return ''.join([tag.spec() for tag in self._tag])
    def set_readonly(self):
        for tag in self._tag:
            tag.set_readonly()
        self._TLIST_READONLY = True
    def set_nodestroy(self):
        self._TLIST_NODESTROY = True
    def draw_tag_tree(self):
        # TODO
        pass
    def draw_tree_leaves(self):
        # TODO
        pass
    def __getitem__(self, index):
        return self._tag[index]
    def __len__(self):
        return len(self._tag)

class TListTest(unittest.TestCase):
    def test(self):
        tlist = TList()
        t1 = Tag("+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言><名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>")
        m1 = Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>")
        t2 = Tag("+ -1D <BGH:解析/かいせき><文末><体言><用言:判><体言止><レベル:C>")
        m2 = Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術\" <代表表記:解析/かいせき>")
        # Add tag with included morpheme
        t1.push_mrph(m1)
        tlist.push_tag(t1)
        self.assertEqual(len(tlist), 1)
        self.assertEqual(len(tlist[0].mrph_list), 1)
        # Add tag without morpheme
        tlist.push_tag(t2)
        self.assertEqual(len(tlist), 2)
        self.assertEqual(len(tlist[1].mrph_list), 0)
        # Add morpheme to second tag
        tlist.push_mrph(m2)
        self.assertEqual(len(tlist), 2)
        self.assertEqual(len(tlist[0].mrph_list), 1)
        self.assertEqual(len(tlist[1].mrph_list), 1)

if __name__ == '__main__':
    unittest.main()
