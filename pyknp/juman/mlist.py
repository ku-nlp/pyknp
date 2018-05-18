#-*- encoding: utf-8 -*-

from __future__ import absolute_import
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
        mid = 1
        if spec != "":
            for line in spec.split("\n"):
                if line.strip() == "":
                    continue
                elif line.startswith('#'):
                    self.comment += line
                elif line.startswith('@') and not line.startswith('@ @'):
                    self._mrph[-1].push_doukei(Morpheme(line[2:], mid))
                    mid += 1
                elif line.startswith('EOS'):
                    pass
                else:
                    self.push_mrph(Morpheme(line, mid))
                    mid += 1

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

    def new_spec(self):
        prev_mids = [0]
        length = 0
        out = []
        for mrph in self._mrph:
            ms = [mrph] + mrph.doukei
            tmp_prev_mids = []
            for m in ms:
                out.append(m.new_spec(prev_mids, length))
                tmp_prev_mids.append(m.mrph_id)
            length += len(mrph.midasi)
            prev_mids = tmp_prev_mids
        return u"".join(out)

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
        self.spec1 = u"""構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 "代表表記:構文/こうぶん カテゴリ:抽象物"\n"""
        self.spec2 = u"""解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術"\n"""
        self.mlist = MList(self.spec1+self.spec2)

    def test_mrph(self):
        self.assertEqual(len(self.mlist), 2)
        self.assertEqual(self.mlist[0].midasi, u'構文')
        self.assertEqual(self.mlist[-1].midasi, u'解析')

    def test_mrph_list(self):
        self.assertEqual(''.join([x.midasi for x in self.mlist]), u'構文解析')
        self.assertEqual(self.mlist.spec(), self.spec1 + self.spec2)
        new_spec = u"""-\t1\t0\t0\t1\t構文\t構文/こうぶん\tこうぶん\t構文\t名詞\t6\t普通名詞\t1\t*\t0\t*\t0\tカテゴリ:抽象物\n""" + \
u"""-\t2\t1\t2\t3\t解析\t解析/かいせき\tかいせき\t解析\t名詞\t6\tサ変名詞\t2\t*\t0\t*\t0\tカテゴリ:抽象物|ドメイン:教育・学習;科学・技術\n"""
        self.assertEqual(self.mlist.new_spec(), new_spec)


    def test_doukei(self):
        spec = u"""母 はは 母 名詞 6 普通名詞 1 * 0 * 0 "代表表記:母/はは 漢字読み:訓 カテゴリ:人 ドメイン:家庭・暮らし"
@ 母 ぼ 母 名詞 6 普通名詞 1 * 0 * 0 "代表表記:母/ぼ 漢字読み:音 カテゴリ:人"
です です だ 判定詞 4 * 0 判定詞 25 デス列基本形 27 NIL
"""
        new_spec = u"""-\t1\t0\t0\t0\t母\t母/はは\tはは\t母\t名詞\t6\t普通名詞\t1\t*\t0\t*\t0\t漢字読み:訓|カテゴリ:人|ドメイン:家庭・暮らし
-\t2\t0\t0\t0\t母\t母/ぼ\tぼ\t母\t名詞\t6\t普通名詞\t1\t*\t0\t*\t0\t漢字読み:音|カテゴリ:人
-\t3\t1;2\t1\t2\tです\tだ/だ\tです\tだ\t判定詞\t4\t*\t0\t判定詞\t25\tデス列基本形\t27\t
"""
        mlist = MList(spec)
        self.assertEqual(mlist.spec(), spec)
        self.assertEqual(mlist.new_spec(), new_spec)


if __name__ == '__main__':
    unittest.main()
