#-*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from pyknp import Morpheme
from pyknp import MList
from pyknp import Tag
from pyknp import TList
import re
import sys
import unittest
from six import u


class Bunsetsu(object):
    """
    KNP による係り受け解析の単位である文節の各種情報を保持するオブジェクト．
    """

    def __init__(self, spec, bnst_id=0, newstyle=False):
        self._mrph_list = MList()
        self._tag_list = TList()
        self.parent_id = -1
        self.parent = None
        self.children = []
        self.dpndtype = ''
        self.fstring = ''
        self._pstring = ''
        self.bnst_id = bnst_id
        spec = spec.strip()
        if spec == '*':
            pass
        elif newstyle:
            items = spec.split(u"\t")
            self.parent_id = int(items[2])
            self.dpndtype = items[3]
            self.fstring = items[17]
            self.repname = items[6]
        elif re.match(r'\* (-?\d+)([DPIA])(.*)$', spec):
            match = re.match(r'\* (-?\d+)([DPIA])(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            sys.stderr.write("Illegal bunsetsu spec: %s\n" % spec)
            quit(1)

        # Extract 正規化代表表記
        if not newstyle:
            self.repname = ''
            match = re.search(r"<正規化代表表記:([^\"\s]+?)>", self.fstring)
            if match:
                self.repname = match.group(1)

    def push_mrph(self, mrph):
        if len(self._tag_list) > 0:
            self._tag_list[-1].push_mrph(mrph)
        self._mrph_list.push_mrph(mrph)

    def push_tag(self, tag):
        if len(self._tag_list) == 0 and len(self._mrph_list) > 0:
            sys.stderr.write("Unsafe addition of tags!\n")
            quit(1)
        self._tag_list.push_tag(tag)

    def spec(self):
        return "* %d%s %s\n%s" % (self.parent_id, self.dpndtype,
                                  self.fstring, self._tag_list.spec())

    def mrph_list(self):
        return self._mrph_list

    def tag_list(self):
        return self._tag_list

    def pstring(self, string=None):
        if string:
            self._pstring = string
        else:
            return self._pstring


class BunsetsuTest(unittest.TestCase):

    def setUp(self):
        self.bunsetsu_str = u"* -1D <BGH:解析/かいせき><文頭><文末>" \
            u"<サ変><体言><用言:判><体言止><レベル:C>"
        self.tag1_str = u"+ 1D <BGH:構文/こうぶん><文節内><係:文節内>" \
            u"<文頭><体言><名詞項候補><先行詞候補>" \
            u"<正規化代表表記:構文/こうぶん>"
        self.mrph1_str = u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"" \
            u"代表表記:構文/こうぶん カテゴリ:抽象物\" " \
            u"<代表表記:構文/こうぶん>"
        self.tag2_str = u"+ -1D <BGH:解析/かいせき><文末><体言>" \
            u"<用言:判><体言止><レベル:C>"
        self.mrph2_str = u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"" \
            u"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;" \
            u"科学・技術\" <代表表記:解析/かいせき>"
        self.spec = u"%s\n%s\n%s\n%s\n%s\n" % (self.bunsetsu_str, self.tag1_str,
                                               self.mrph1_str, self.tag2_str,
                                               self.mrph2_str)

    def test_simple(self):
        bnst = Bunsetsu(self.bunsetsu_str, 3)
        self.assertEqual(bnst.bnst_id, 3)
        self.assertEqual(bnst.parent_id, -1)
        self.assertEqual(bnst.dpndtype, "D")
        self.assertEqual(len(bnst.mrph_list()), 0)
        self.assertEqual(len(bnst.tag_list()), 0)

    def test_mrph(self):
        bnst = Bunsetsu(self.bunsetsu_str)
        mrph1 = Morpheme(self.mrph1_str)
        bnst.push_mrph(mrph1)
        self.assertEqual(len(bnst.mrph_list()), 1)
        mrph2 = Morpheme(self.mrph2_str)
        bnst.push_mrph(mrph2)
        self.assertEqual(len(bnst.mrph_list()), 2)
        self.assertEqual(''.join(mrph.midasi for mrph in bnst.mrph_list()),
                         u'構文解析')

    def test_spec(self):
        bnst = Bunsetsu(self.bunsetsu_str)
        tag1 = Tag(self.tag1_str)
        mrph1 = Morpheme(self.mrph1_str)
        tag1.push_mrph(mrph1)
        bnst.push_tag(tag1)
        tag2 = Tag(self.tag2_str)
        mrph2 = Morpheme(self.mrph2_str)
        tag2.push_mrph(mrph2)
        bnst.push_tag(tag2)
        self.assertEqual(bnst.spec(), self.spec)

if __name__ == '__main__':
    unittest.main()
