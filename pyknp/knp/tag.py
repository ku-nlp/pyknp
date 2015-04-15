#-*- encoding: utf-8 -*-

from pyknp import MList
from pyknp import Morpheme
import re
import sys
import unittest

class Tag(object):
    def __init__(self, spec, tag_id=0):
        self.mrph_list = MList()
        self.parent_id = -1
        self.dpndtype = ''
        self.fstring = ''
        self.tag_id = tag_id
        spec = spec.strip()
        if spec == '+':
            pass
        elif re.match(r'\+ (-?\d+)(\w)(.*)$', spec):
            match = re.match(r'\+ (-?\d+)(\w)(.*)$', spec)
            self.parent_id = int(match.group(1))
            self.dpndtype = match.group(2)
            self.fstring = match.group(3).strip()
        else:
            sys.stderr.write("Illegal tag spec: %s\n" % spec)
            quit(1)
    def push_mrph(self, mrph):
        self.mrph_list.push_mrph(mrph)
    def spec(self):
        return "+ %d%s %s\n%s" % (self.parent_id, self.dpndtype, self.fstring,
                                  self.mrph_list.spec())

class TagTest(unittest.TestCase):
    def test(self):
        tag_str = u"+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>" \
                u"<名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        tag = Tag(tag_str, 2)
        self.assertEqual(tag.tag_id, 2)
        self.assertEqual(tag.dpndtype, 'D')
        self.assertEqual(tag.parent_id, 1)
        self.assertEqual(len(tag.mrph_list), 0)
        mrph1 = Morpheme(u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"" \
                u"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>")
        mrph2 = Morpheme(u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"" \
                u"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育" \
                u"・学習;科学・技術\" <代表表記:解析/かいせき>")
        tag.push_mrph(mrph1)
        self.assertEqual(len(tag.mrph_list), 1)
        tag.push_mrph(mrph2)
        self.assertEqual(len(tag.mrph_list), 2)
        self.assertEqual(''.join([mrph.midasi for mrph in tag.mrph_list]),
                         u'構文解析')

if __name__ == '__main__':
    unittest.main()
