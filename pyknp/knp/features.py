#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from pyknp import Pas
from pyknp import Rel
import unittest
import six


class Features(dict):
    """
    タグ(基本句)のfeatureを保持するオブジェクト
    """

    def __init__(self, spec, splitter=u"><", ignore_first_character=True):
        assert isinstance(spec, six.text_type)

        self.spec = spec.rstrip()
        self.pas = None
        self.rels = None
        if len(spec) == 0:
            return

        tag_start = 0
        if ignore_first_character:
            tag_start = 1
        tag_end = None
        while tag_end != -1:
            tag_end = self.spec.find(splitter, tag_start)
            kv_splitter = self.spec.find(u':', tag_start, tag_end)
            if self.spec[tag_start:].startswith(u'rel '):
                rel = Rel(self.spec[tag_start:tag_end])
                if rel.ignore == False:
                    if self.rels is None:
                        self.rels = []
                    self.rels.append(rel)
            elif kv_splitter == -1:
                key = self.spec[tag_start:tag_end]
                val = True  # Dummy value
                self[key] = val
            else:
                key = self.spec[tag_start: kv_splitter]
                val = self.spec[kv_splitter + 1: tag_end]
                self[key] = val

                if key == u'格解析結果':
                    self.pas = Pas(val, knpstyle=True)

            tag_start = tag_end + len(splitter)


class FeaturesTest(unittest.TestCase):

    def test(self):
        tag_str1 = u"<BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>" \
            u"<名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        f1 = Features(tag_str1)
        self.assertEqual(f1.get(u"BGH"), u"構文/こうぶん")
        self.assertEqual(f1.get(u"係"), u"文節内")
        self.assertEqual(f1.get(u"先行詞候補"), True)
        self.assertEqual(f1.get(u"dummy"), None)
        self.assertEqual(f1.get(u"正規化代表表記"), u"構文/こうぶん")

    def testPAS(self):
        pas_input = u"分/ふん:判1:ガ/U/-/-/-/-;ヲ/U/-/-/-/-;ニ/U/-/-/-/-;デ/C/車/1/0/14;デ/C/徒歩/7/0/17;カラ/U/-/-/-/-;ヨリ/C/インター/0/0/14;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-"
        tag_str2 = u"""<文末><カウンタ:分><時間><強時間><数量><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><修飾><提題受:30><主節><状態述語><判定詞><正規化代表表記:３/さん+分/ふん><用言代表表記:分/ふん><時制-無時制><格関係0:ヨリ:インター><格関係1:デ:車><格解析結果:%s>""" % pas_input
        f2 = Features(tag_str2)
        self.assertEqual(f2.get(u"格解析結果"), pas_input)
        self.assertEqual(f2.pas.cfid, u"分/ふん:判1")
        f2args = f2.pas.arguments
        self.assertEqual(len(f2args), 2)
        self.assertEqual(len(f2args.get(u"デ")), 2)
        self.assertEqual(f2args.get(u"デ")[0].rep, u"車")
        self.assertEqual(f2args.get(u"デ")[0].tid, 1)
        self.assertEqual(f2args.get(u"デ")[0].sid, u"14")
        self.assertEqual(f2args.get(u"デ")[1].rep, u"徒歩")
        self.assertEqual(f2args.get(u"デ")[1].tid, 7)
        self.assertEqual(f2args.get(u"デ")[1].sid, u"17")
        self.assertEqual(len(f2args.get(u"ヨリ")), 1)
        self.assertEqual(f2args.get(u"ガ"), None)
        self.assertEqual(f2.rels, None)

    def testRels(self):
        tag_str = u"""<rel type="時間" target="一九九五年" sid="950101003-002" id="1"/>""" +  \
            u"""<rel type="ヲ" target="衆院" sid="950101003-002" id="3"/>""" +\
            u"""<rel type="ガ" target="不特定:人1"/>""" +\
            u"""<rel type="時間" target="国会前" sid="950101003-asd" id="16"/>"""

        f = Features(tag_str)
        self.assertEqual(f.pas, None)
        self.assertEqual(len(f.rels), 4)
        self.assertEqual(f.rels[0].tid, 1)
        self.assertEqual(f.rels[0].mode, u"")
        self.assertEqual(f.rels[0].atype, u"時間")
        self.assertEqual(f.rels[0].sid, u"950101003-002")
        self.assertEqual(f.rels[0].target, u"一九九五年")


if __name__ == '__main__':
    unittest.main()
