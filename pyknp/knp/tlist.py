#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import Morpheme
from pyknp import Tag
from pyknp import DrawTree
import sys
import unittest


class TList(DrawTree):

    def __init__(self):
        self._tag = []
        self._readonly = False

    def push_tag(self, tag):
        if not self._readonly:
            self._tag.append(tag)

    def push_mrph(self, mrph):
        if len(self._tag) > 0:
            self._tag[-1].push_mrph(mrph)
        else:
            sys.stderr.write("Cannot push mrph: no tags.")
            quit(1)

    def push_synnodes(self, synnodes):
        if len(self._tag) > 0:
            self._tag[-1].synnodes.append(synnodes)
        else:
            sys.stderr.write("Cannot push synnodes: no tags.")
            quit(1)

    def push_synnode(self, synnode):
        if len(self._tag) > 0:
            self._tag[-1].synnodes[-1].synnode.append(synnode)
        else:
            sys.stderr.write("Cannot push synnode: no tags.")
            quit(1)

    def spec(self):
        return ''.join([tag.spec() for tag in self._tag])

    def set_readonly(self):
        for tag in self._tag:
            tag.set_readonly()
        self._readonly = True

    def draw_tag_tree(self):
        """ タグ列の依存関係を木構造として表現して出力する． """
        self.draw_tree()

    def draw_tree_leaves(self):
        """ draw_tree メソッドとの通信用のメソッド． """
        return self.tag_list()

    def tag_list(self):
        return self._tag

    def __getitem__(self, index):
        return self._tag[index]

    def __len__(self):
        return len(self._tag)


class TListTest(unittest.TestCase):

    def test(self):
        tlist = TList()
        tag1 = Tag(u"+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭>"
                   u"<体言><名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>")
        mrph1 = Morpheme(u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \""
                         u"代表表記:構文/こうぶん カテゴリ:抽象物\" "
                         u"<代表表記:構文/こうぶん>")
        tag2 = Tag(u"+ -1D <BGH:解析/かいせき><文末><体言><用言:判>"
                   u"<体言止><レベル:C>")
        mrph2 = Morpheme(u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \""
                         u"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;"
                         u"科学・技術\" <代表表記:解析/かいせき>")
        # Add tag with included morpheme
        tag1.push_mrph(mrph1)
        tlist.push_tag(tag1)
        self.assertEqual(len(tlist), 1)
        self.assertEqual(len(tlist[0].mrph_list()), 1)
        # Add tag without morpheme
        tlist.push_tag(tag2)
        self.assertEqual(len(tlist), 2)
        self.assertEqual(len(tlist[1].mrph_list()), 0)
        # Add morpheme to second tag
        tlist.push_mrph(mrph2)
        self.assertEqual(len(tlist), 2)
        self.assertEqual(len(tlist[0].mrph_list()), 1)
        self.assertEqual(len(tlist[1].mrph_list()), 1)

if __name__ == '__main__':
    unittest.main()
