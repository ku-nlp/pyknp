#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest


def parsePAS(val):
    c0 = val.find(u':')
    c1 = val.find(u':', c0 + 1)
    cfid = val[:c0] + u":" + val[c0 + 1:c1]
    pas = {u"cfid": cfid, u"arguments": {}}

    if val.count(u":") < 2:  # For copula
        return

    for k in val[c1 + 1:].split(u';'):
        items = k.split(u"/")
        if items[1] != u"U" and items[1] != u"-":
            mycase = items[0]
            mycasetype = items[1]
            myarg = items[2]
            myarg_no = int(items[3])
            myarg_sent_id = int(items[5])

            pas[u"arguments"][mycase] = {
                u"no": myarg_no, u"type": mycasetype, u"arg": myarg, u"sid": myarg_sent_id}
    return pas


import re
REL_PAT = "rel type=\"([^\s]+?)\"(?: mode=\"([^>]+?)\")? target=\"([^\s]+?)\"(?: sid=\"(.+?)\" id=\"(.+?)\")?/"
WRITER_READER_LIST = [u"著者", u"読者"]
WRITER_READER_CONV_LIST = {u"一人称": u"著者", u"二人称": u"読者"}


def parseRel(fstring, consider_writer_reader=False):
    for match in re.findall(r"%s" % REL_PAT, fstring):
        atype, mode, target, sid, id = match
        if mode == u"？":
            continue

        if consider_writer_reader:
            if not sid:
                if target == u"なし":
                    continue
                if target in WRITER_READER_CONV_LIST:
                    target = WRITER_READER_CONV_LIST[target]

                if target not in WRITER_READER_LIST:
                    continue  # XXX
                sid = target_sid  # dummy
                id = None  # dummy
        else:
            if not sid:
                continue

        if id is not None:
            id = int(id)

        data = {"type": atype, "target": target,
                "sid": sid, "id": id, "mode": mode}
        return data


class Features(dict):
    """
    タグ(基本句)のfeatureを保持するオブジェクト
    """

    def __init__(self, spec, splitter=u"><", ignore_first_character=True):
        assert isinstance(spec, unicode)

        self.spec = spec.rstrip()
        self.pas = None
        self.rels = None

        tag_start = 0
        if ignore_first_character:
            tag_start = 1
        tag_end = None
        while tag_end != -1:
            tag_end = self.spec.find(splitter, tag_start)
            kv_splitter = self.spec.find(u':', tag_start, tag_end)
            if self.spec[tag_start:].startswith(u'rel '):
                rel = parseRel(self.spec[tag_start:tag_end])
                if rel is not None:
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
                    self.pas = parsePAS(val)

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
        pas_input = u"分/ふん:判1:ガ/U/-/-/-/-;ヲ/U/-/-/-/-;ニ/U/-/-/-/-;デ/C/車/1/0/14;カラ/U/-/-/-/-;ヨリ/C/インター/0/0/14;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-"
        tag_str2 = u"""<文末><カウンタ:分><時間><強時間><数量><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><修飾><提題受:30><主節><状態述語><判定詞><正規化代表表記:３/さん+分/ふん><用言代表表記:分/ふん><時制-無時制><格関係0:ヨリ:インター><格関係1:デ:車><格解析結果:%s>""" % pas_input
        f2 = Features(tag_str2)
        self.assertEqual(f2.get(u"格解析結果"), pas_input)
        self.assertEqual(f2.pas.get(u"cfid"), u"分/ふん:判1")
        f2args = f2.pas.get(u"arguments")
        self.assertEqual(len(f2args), 2)
        self.assertEqual(f2args.get(u"デ").get(u"no"), 1)
        self.assertEqual(f2args.get(u"デ").get(u"type"), u"C")
        self.assertEqual(f2args.get(u"デ").get(u"arg"), u"車")
        self.assertEqual(f2args.get(u"デ").get(u"sid"), 14)
        self.assertEqual(f2args.get(u"ガ"), None)
        self.assertEqual(f2.rels, None)

    def testRels(self):
        tag_str = u"""<rel type="時間" target="一九九五年" sid="950101003-002" id="1"/>""" +  \
            u"""<rel type="ヲ" target="衆院" sid="950101003-002" id="3"/>""" +\
            u"""<rel type="ガ" target="不特定:人1"/>""" +\
            u"""<rel type="時間" target="国会前" sid="950101003-asd" id="16"/>"""

        f = Features(tag_str)
        self.assertEqual(f.pas, None)
        self.assertEqual(len(f.rels), 3)
        self.assertEqual(f.rels[0].get(u"id"), 1)
        self.assertEqual(f.rels[0].get(u"mode"), u"")
        self.assertEqual(f.rels[0].get(u"type"), u"時間")
        self.assertEqual(f.rels[0].get(u"sid"), u"950101003-002")
        self.assertEqual(f.rels[0].get(u"target"), u"一九九五年")


if __name__ == '__main__':
    unittest.main()
