#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import MList
from pyknp import Morpheme
from pyknp import Features
import re
import sys
import unittest


class Tag(object):
    """
    格解析の単位となるタグ(基本句)の各種情報を保持するオブジェクト．
    """

    def __init__(self, spec, tag_id=0, newstyle=False):
        self._mrph_list = MList()
        self.parent_id = -1
        self.parent = None
        self.children = []
        self.dpndtype = ''
        self.fstring = ''
        self.features = None
        self._pstring = ''
        self.tag_id = tag_id
        self.synnodes = []
        spec = spec.strip()
        if spec == '+':
            pass
        elif newstyle:
            items = spec.split(u"\t")
            self.parent_id = int(items[2])
            self.dpndtype = items[3]
            self.fstring = items[17]
            self.repname = items[6]
            self.features = Features(self.fstring, u"|", False)
        elif re.match(r'\+ (-?\d+)(\w)(.*)$', spec):
            match = re.match(r'\+ (-?\d+)(\w)(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            sys.stderr.write("Illegal tag spec: %s\n" % spec)
            quit(1)

        # Extract 正規化代表表記
        if not newstyle:
            self.repname = ''
            self.features = Features(self.fstring)
            rep = self.features.get(u"正規化代表表記")
            if rep is not None:
                self.repname = rep

    def push_mrph(self, mrph):
        self._mrph_list.push_mrph(mrph)

    def spec(self):
        return "+ %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring,
                                  self._mrph_list.spec())

    def mrph_list(self):
        return self._mrph_list

    def pstring(self, string=None):
        if string:
            self._pstring = string
        else:
            return self._pstring

    def get_surface(self):
        return ''.join([mrph.midasi for mrph in self.mrph_list()])


class TagTest(unittest.TestCase):

    def test(self):
        tag_str = u"+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>" \
            u"<名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        tag = Tag(tag_str, 2)
        self.assertEqual(tag.tag_id, 2)
        self.assertEqual(tag.dpndtype, 'D')
        self.assertEqual(tag.parent_id, 1)
        self.assertEqual(len(tag.mrph_list()), 0)
        mrph1 = Morpheme(u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \""
                         u"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>")
        mrph2 = Morpheme(u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \""
                         u"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育"
                         u"・学習;科学・技術\" <代表表記:解析/かいせき>")
        tag.push_mrph(mrph1)
        self.assertEqual(len(tag.mrph_list()), 1)
        tag.push_mrph(mrph2)
        self.assertEqual(len(tag.mrph_list()), 2)
        self.assertEqual(tag.get_surface(), u'構文解析')

if __name__ == '__main__':
    unittest.main()
