#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from pyknp import Rel
import unittest
import six


class Features(dict):
    """ feature情報を保持するオブジェクト

    feature情報に含まれるタグをパースし、辞書形式にする。
    ex. "<正規化代表表記:遅れる/おくれる>" --> {"正規化代表表記": "遅れる/おくれる"}
    """

    def __init__(self, spec, splitter="><", ignore_first_character=True):
        assert isinstance(spec, six.text_type)

        self.spec = spec.rstrip()
        self.rels = None
        self._tag = None
        if len(spec) == 0:
            return

        tag_start = 0
        if ignore_first_character:
            tag_start = 1
        tag_end = None
        while tag_end != -1:
            tag_end = self.spec.find(splitter, tag_start)
            kv_splitter = self.spec.find(':', tag_start, tag_end)
            if self.spec[tag_start:].startswith('rel '):
                rel = Rel(self.spec[tag_start:tag_end])
                if rel.ignore is False:
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

            tag_start = tag_end + len(splitter)

    @property
    def pas(self):
        return self._tag.pas


class FeaturesTest(unittest.TestCase):

    def test(self):
        tag_str1 = "<BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>" +\
            "<名詞項候補><先行詞候補><正規化代表表記:構文/こうぶん>"
        f1 = Features(tag_str1)
        self.assertEqual(f1.get("BGH"), "構文/こうぶん")
        self.assertEqual(f1.get("係"), "文節内")
        self.assertEqual(f1.get("先行詞候補"), True)
        self.assertEqual(f1.get("dummy"), None)
        self.assertEqual(f1.get("正規化代表表記"), "構文/こうぶん")

    def testRels(self):
        tag_str = """<rel type="時間" target="一九九五年" sid="950101003-002" id="1"/>""" +  \
            """<rel type="ヲ" target="衆院" sid="950101003-002" id="3"/>""" +\
            """<rel type="ガ" target="不特定:人1"/>""" +\
            """<rel type="時間" target="国会前" sid="950101003-asd" id="16"/>"""

        f = Features(tag_str)
        self.assertEqual(len(f.rels), 4)
        self.assertEqual(f.rels[0].tid, 1)
        self.assertEqual(f.rels[0].mode, "")
        self.assertEqual(f.rels[0].atype, "時間")
        self.assertEqual(f.rels[0].sid, "950101003-002")
        self.assertEqual(f.rels[0].target, "一九九五年")


if __name__ == '__main__':
    unittest.main()
