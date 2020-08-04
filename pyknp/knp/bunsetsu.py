# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from pyknp import Morpheme, JUMAN_FORMAT
from pyknp import MList
from pyknp import Tag
from pyknp import TList
from pyknp import Features
import re
import unittest


class Bunsetsu(object):
    """
    KNP による係り受け解析の単位である文節の各種情報を保持するオブジェクト．

    Args:
        spec (str): KNP出力のうち文節に該当する箇所の文字列
        bnst_id (int): 文節ID
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

    Attributes:
        bnst_id (int): 文節ID
        midasi (str): 見出し
        parent (Bunsetsu): 親の文節オブジェクト
        parent_id (int): 親の文節ID
        children (list): 子の文節オブジェクトのリスト
        repname (str): 正規化代表表記 (normalized_repnameに同じ)
        normalized_repname (str): 正規化代表表記
        head_repname (str): 主辞代表表記
        head_prime_repname (str): 主辞’代表表記
        fstring (str): feature情報
    """

    def __init__(self, spec, bnst_id=0, juman_format=JUMAN_FORMAT.DEFAULT):
        self._mrph_list = MList()
        self._tag_list = TList()
        self.midasi = ''
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
        elif juman_format != JUMAN_FORMAT.DEFAULT:  # TODO
            items = spec.split("\t")
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
            raise Exception("Illegal bunsetsu spec: %s" % spec)
        self.features = Features(self.fstring)

        # Extract 正規化代表表記
        if juman_format == JUMAN_FORMAT.DEFAULT:
            self.repname = ''
            self.normalized_repname = ''
            self.head_repname = ''
            self.head_prime_repname = ''

            normalized_repname = self.features.get("正規化代表表記")
            if normalized_repname:
                self.repname = normalized_repname
                self.normalized_repname = normalized_repname
            head_repname = self.features.get("主辞代表表記")
            if head_repname:
                self.head_repname = head_repname
            head_prime_repname = self.features.get("主辞’代表表記")
            if head_prime_repname:
                self.head_prime_repname = head_prime_repname

    def push_mrph(self, mrph):
        """ 新しい形態素オブジェクトをセットする """
        if len(self._tag_list) > 0:
            self._tag_list[-1].push_mrph(mrph)
        self._mrph_list.push_mrph(mrph)

    def push_tag(self, tag):
        """ 新しい基本句オブジェクトをセットする """
        if len(self._tag_list) == 0 and len(self._mrph_list) > 0:
            raise Exception("Unsafe addition of tags!")
        self._tag_list.push_tag(tag)

    def set_midasi(self):
        """ midasiをセットする """
        for i in range(len(self._tag_list)):
            self._tag_list[i].set_midasi()
        self.midasi = ''.join(mrph.midasi for mrph in self.mrph_list())

    def spec(self):
        """ 文節に対応するKNP出力 """
        return "* %d%s %s\n%s" % (self.parent_id, self.dpndtype,
                                  self.fstring, self._tag_list.spec())

    def mrph_list(self):
        """ 文節を構成する全形態素オブジェクトを返す

        Returns:
            list: 形態素オブジェクトMorphemeのリスト
        """
        return self._mrph_list

    def tag_list(self):
        """ 文節を構成する全基本句オブジェクトを返す

        Returns:
            list: 基本句オブジェクトTagのリスト
        """
        return self._tag_list

    def pstring(self, string=None):
        """ draw_treeしたときに右側に出力する文字列を返す """
        if string:
            self._pstring = string
        else:
            return self._pstring


class BunsetsuTest(unittest.TestCase):

    def setUp(self):
        self.bunsetsu_str = "* -1D <BGH:解析/かいせき><文頭><文末>" \
            "<サ変><体言><用言:判><体言止><レベル:C>"
        self.tag1_str = "+ 1D <BGH:構文/こうぶん><文節内><係:文節内>" \
            "<文頭><体言><名詞項候補><先行詞候補>" \
            "<正規化代表表記:構文/こうぶん>"
        self.mrph1_str = "構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"" \
            "代表表記:構文/こうぶん カテゴリ:抽象物\" " \
            "<代表表記:構文/こうぶん>"
        self.tag2_str = "+ -1D <BGH:解析/かいせき><文末><体言>" \
            "<用言:判><体言止><レベル:C>"
        self.mrph2_str = "解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"" \
            "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;" \
            "科学・技術\" <代表表記:解析/かいせき>"
        self.spec = "%s\n%s\n%s\n%s\n%s\n" % (self.bunsetsu_str, self.tag1_str,
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
                         '構文解析')

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
