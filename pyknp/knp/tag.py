# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from pyknp import MList
from pyknp import Morpheme, JUMAN_FORMAT
from pyknp import Features
import re
import unittest


class Tag(object):
    """
    ある文に関する基本句列を保持するオブジェクト

    Args:
        spec (str): KNP出力
        tag_id (int): 基本句ID
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

    Attributes:
        tag_id (int): 基本句ID
        midasi (str): 見出し
        parent (Tag): 親の基本句オブジェクト
        parent_id (int): 親の基本句ID
        children (list): 子の基本句オブジェクトのリスト
        dpndtype (str): 係り受けタイプ
        fstring (str): feature情報
        repname (str): 正規化代表表記 (normalized_repnameに同じ)
        normalized_repname (str): 正規化代表表記
        head_repname (str): 主辞代表表記
        head_prime_repname (str): 主辞’代表表記
        pred_repname (str): 用言代表表記
        disambiguated_pred_repname (str): 標準用言代表表記
        features (Features): 基本句のfeatureを表すFeatureオブジェクト
        pas (Pas): 基本句が述語の場合は項の情報(Pasオブジェクト), そうでない場合None
    """

    def __init__(self, spec, tag_id=0, juman_format=JUMAN_FORMAT.DEFAULT):
        self._mrph_list = MList()
        self.midasi = ''
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
        elif juman_format != JUMAN_FORMAT.DEFAULT:
            items = spec.split("\t")
            self.parent_id = int(items[2])
            self.dpndtype = items[3]
            self.fstring = items[17]
            self.repname = items[6]
            self.features = Features(self.fstring, "|", False)
            self.features._tag = self
        elif re.match(r'\+ (-?\d+)(\w)(.*)$', spec):
            match = re.match(r'\+ (-?\d+)(\w)(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            raise Exception("Illegal tag spec: %s" % spec)

        # Extract 正規化代表表記
        if juman_format == JUMAN_FORMAT.DEFAULT:
            self.repname = ''
            self.normalized_repname = ''
            self.head_repname = ''
            self.head_prime_repname = ''
            self.pred_repname = ''
            self.disambiguated_pred_repname = ''

            self.features = Features(self.fstring)
            self.features._tag = self

            normalized_repname = self.features.get("正規化代表表記")
            if normalized_repname is not None:
                self.repname = normalized_repname
                self.normalized_repname = normalized_repname
            head_repname = self.features.get("主辞代表表記")
            if head_repname is not None:
                self.head_repname = head_repname
            head_prime_repname = self.features.get("主辞’代表表記")
            if head_prime_repname:
                self.head_prime_repname = head_prime_repname
            pred_repname = self.features.get("用言代表表記")
            if pred_repname is not None:
                self.pred_repname = pred_repname
            disambiguated_pred_repname = self.features.get("標準用言代表表記")
            if disambiguated_pred_repname is not None:
                self.disambiguated_pred_repname = disambiguated_pred_repname

    def push_mrph(self, mrph):
        """ 新しい形態素オブジェクトをセットする """
        self._mrph_list.push_mrph(mrph)

    def set_midasi(self):
        """ midasiをセットする """
        self.midasi = self.get_surface()

    def spec(self):
        """ 基本句に対応するKNP出力 """
        return "+ %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring,
                                  self._mrph_list.spec())

    def mrph_list(self):
        """ 基本句を構成する全形態素オブジェクトを返す

        Returns:
            list: 形態素オブジェクトMorphemeのリスト
        """
        return self._mrph_list

    def pstring(self, string=None):
        """ draw_treeしたときに右側に出力する文字列を返す """
        if string:
            self._pstring = string
        else:
            return self._pstring

    def get_surface(self):
        """ 基本句の見出しを返す

        Returns:
            str: 基本句の見出し
        """
        return ''.join(mrph.midasi for mrph in self.mrph_list())


class TagTest(unittest.TestCase):

    def test(self):
        tag_str = "+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>" \
            "<名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        tag = Tag(tag_str, 2)
        self.assertEqual(tag.tag_id, 2)
        self.assertEqual(tag.dpndtype, 'D')
        self.assertEqual(tag.parent_id, 1)
        self.assertEqual(len(tag.mrph_list()), 0)
        mrph1 = Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \""
                         "代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>")
        mrph2 = Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \""
                         "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育"
                         "・学習;科学・技術\" <代表表記:解析/かいせき>")
        tag.push_mrph(mrph1)
        self.assertEqual(len(tag.mrph_list()), 1)
        tag.push_mrph(mrph2)
        self.assertEqual(len(tag.mrph_list()), 2)
        self.assertEqual(tag.get_surface(), '構文解析')


if __name__ == '__main__':
    unittest.main()
