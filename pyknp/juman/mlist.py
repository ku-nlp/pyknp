#-*- encoding: utf-8 -*-

from pyknp import Morpheme
import unittest

class MList(object):
    def __init__(self, mrphs=[]):
        self._mrph = []
        for mrph in mrphs:
            self._mrph.append(mrph)
        self._readonly = False
    def push_mrph(self, mrph):
        if self._readonly:
            return
        self._mrph.append(mrph)
    def set_readonly(self):
        self._readonly = True
    def spec(self):
        spec = ""
        for mrph in self._mrph:
            spec = "%s%s" % (spec, mrph.spec())
            for doukei in mrph.doukei:
                spec = "%s@ %s" % (spec, doukei.spec())
        return spec
    def mrph_list(self):
        return self._mrph
    def __getitem__(self, index):
        return self._mrph[index]
    def __len__(self):
        return len(self._mrph)

class MListTest(unittest.TestCase):
    def setUp(self):
        self.mlist = MList()
        self.mlist.push_mrph(Morpheme(u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0\n"))
        self.mlist.push_mrph(Morpheme(u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0\n"))
    def test_mrph(self):
        self.assertEqual(len(self.mlist), 2)
        self.assertEqual(self.mlist[0].midasi, u'構文')
        self.assertEqual(self.mlist[-1].midasi, u'解析')
    def test_mrph_list(self):
        self.assertEqual(''.join([x.midasi for x in self.mlist]), u'構文解析')

if __name__ == '__main__':
    unittest.main()
