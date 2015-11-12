#-*- encoding: utf-8 -*-

from pyknp import Morpheme
import unittest


class MList(object):
    """
    形態素列を保持するオブジェクト．
    """

    def __init__(self, spec=""):
        self._mrph = []
        self._readonly = False
        self.comment = ""
        if spec != "":
            for line in spec.split("\n"):
                if line.strip() == "":
                    continue
                elif line.startswith('#'):
                    self.comment += line
                elif line.startswith('@'):
                    self._mrph[-1].push_doukei(Morpheme(line[2:]))
                elif line.startswith('EOS'):
                    pass
                else:
                    self.push_mrph(Morpheme(line, len(self._mrph)))

    def push_mrph(self, mrph):
        if self._readonly:
            return
        self._mrph.append(mrph)

    def set_readonly(self):
        self._readonly = True

    def spec(self):
        """
        形態素列の全文字列を返す．Juman による出力と同じ形式の結果が得られる．
        """
        spec = ""
        for mrph in self._mrph:
            spec = "%s%s" % (spec, mrph.spec())
            for doukei in mrph.doukei:
                spec = "%s@ %s" % (spec, doukei.spec())
        return spec

    def mrph_list(self):
        """
        全ての形態素のリストを返す．
        """
        return self._mrph

    def __getitem__(self, index):
        return self._mrph[index]

    def __len__(self):
        return len(self._mrph)


class MListTest(unittest.TestCase):

    def setUp(self):
        self.mlist = MList()
        self.spec1 = u"""構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 "代表表記:構文/こうぶん カテゴリ:抽象物"\n"""
        self.spec2 = u"""解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術"\n"""
        self.mlist.push_mrph(Morpheme(self.spec1))
        self.mlist.push_mrph(Morpheme(self.spec2))

    def test_mrph(self):
        self.assertEqual(len(self.mlist), 2)
        self.assertEqual(self.mlist[0].midasi, u'構文')
        self.assertEqual(self.mlist[-1].midasi, u'解析')

    def test_mrph_list(self):
        self.assertEqual(''.join([x.midasi for x in self.mlist]), u'構文解析')
        self.assertEqual(self.mlist.spec(), self.spec1 + self.spec2)


if __name__ == '__main__':
    unittest.main()
