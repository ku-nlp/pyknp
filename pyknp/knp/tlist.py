# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from pyknp import Morpheme
from pyknp import Tag
from pyknp import draw_tree, sprint_tree
import unittest


class TList(object):
    """ ある文に関する基本句列を保持するオブジェクト """

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
            raise Exception("Cannot push mrph: no tags.")

    def push_synnodes(self, synnodes):
        if len(self._tag) > 0:
            self._tag[-1].synnodes.append(synnodes)
        else:
            raise Exception("Cannot push synnodes: no tags.")

    def push_synnode(self, synnode):
        if len(self._tag) > 0:
            self._tag[-1].synnodes[-1].synnode.append(synnode)
        else:
            raise Exception("Cannot push synnode: no tags.")

    def spec(self):
        return ''.join([tag.spec() for tag in self._tag])

    def set_readonly(self):
        for tag in self._tag:
            tag.set_readonly()
        self._readonly = True

    def draw_tree(self, fh=None, show_pos=True):
        self.draw_tag_tree(fh=fh, show_pos=show_pos)

    def draw_tag_tree(self, fh=None, show_pos=True):
        """ タグ列の依存関係を木構造として表現して出力する． """
        draw_tree(self._tag, fh=fh, show_pos=show_pos)

    def sprint_tree(self):
        return sprint_tree(self._tag)

    def tag_list(self):
        """ 基本句列を構成する全基本句オブジェクトを返す

        Returns:
            list of Tag: 基本句オブジェクトTagのリスト
        """
        return self._tag

    def __getitem__(self, index):
        return self._tag[index]

    def __len__(self):
        return len(self._tag)


class TListTest(unittest.TestCase):

    def test(self):
        tlist = TList()
        tag1 = Tag("+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭>"
                   "<体言><名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>")
        mrph1 = Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \""
                         "代表表記:構文/こうぶん カテゴリ:抽象物\" "
                         "<代表表記:構文/こうぶん>")
        tag2 = Tag("+ -1D <BGH:解析/かいせき><文末><体言><用言:判>"
                   "<体言止><レベル:C>")
        mrph2 = Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \""
                         "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;"
                         "科学・技術\" <代表表記:解析/かいせき>")
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
