#-*- encoding: utf-8 -*-

import unittest
from morpheme import Morpheme

class MList:
    def __init__(self, mrphs=[]):
        self.mrph = []
        for mrph in mrphs:
            self.push_mrph(mrph)
        self.MLIST_READONLY = False
    def mrph_list(self):
        return self.mrph
    def push_mrph(self, mrph):
        if self.MLIST_READONLY:
            return
        self.mrph.append(mrph)
    def set_readonly(self):
        self.MLIST_READONLY = True
    def set_mlist_readonly(self):
        self.set_readonly()
    def spec(self):
        spec = ""
        for mrph in self.mrph:
            spec = "%s%s" % (spec, mrph.spec())
            for doukei in mrph.doukei:
                spec = "%s@ %s" % (spec, doukei.spec())
        return spec

class MListTest(unittest.TestCase):
    def setUp(self):
        self.mlist = MList()
        self.mlist.push_mrph(Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0\n"))
        self.mlist.push_mrph(Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0\n"))
    def test_mrph(self):
        self.assertEqual(len(self.mlist.mrph), 2)
        self.assertEqual(self.mlist.mrph[0].midasi, '構文')
        self.assertEqual(self.mlist.mrph[-1].midasi, '解析')
    def test_mrph_list(self):
        self.assertEqual(''.join([x.midasi for x in self.mlist.mrph_list()]), '構文解析')

if __name__ == '__main__':
    unittest.main()
