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
    ある文に関する基本句列を保持するオブジェクト

    Attributes:
        tag_id (int): 基本句ID
        parent (Tag): 親の基本句オブジェクト
        parent_id (int): 親の基本句ID
        children (list): 子の基本句オブジェクトのリスト
        dpndtype (str): 係り受けタイプ
        fstring (str): feature情報
        features (Features): 基本句のfeatureを表すFeatureオブジェクト
        pas (Pas): 基本句が述語の場合は項の情報(Pasオブジェクト), そうでない場合None
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
        self.pas = None
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
            self.features._tag = self
        elif re.match(r'\+ (-?\d+)(\w)(.*)$', spec):
            match = re.match(r'\+ (-?\d+)(\w)(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            raise Exception("Illegal tag spec: %s" % spec)

        # Extract 正規化代表表記
        if not newstyle:
            self.repname = ''
            self.features = Features(self.fstring)
            self.features._tag = self
            rep = self.features.get(u"正規化代表表記")
            if rep is not None:
                self.repname = rep

    def push_mrph(self, mrph):
        self._mrph_list.push_mrph(mrph)

    def spec(self):
        return "+ %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring,
                                  self._mrph_list.spec())

    def mrph_list(self):
        """ 基本句を構成する全形態素オブジェクトを返す

        Returns:
            list: 形態素オブジェクトMorphemeのリスト
        """
        return self._mrph_list

    def pstring(self, string=None):
        if string:
            self._pstring = string
        else:
            return self._pstring

    def get_surface(self):
        """ 基本句の見出しを返す

        Returns:
            str: 基本句の見出し
        """
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
