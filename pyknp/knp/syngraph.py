# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
import re
import unittest


class SynNodes(object):

    def __init__(self, spec):
        self.tagids = []
        self.parentids = []
        self.dpndtype = ''
        self.midasi = ''
        self.feature = ''
        self.synnode = []

        # !! 0 1D <見出し:国際化が><格解析結果:ガ格>
        tagid, dpnd, string = spec.split(' ')[1:4]
        self.tagids = [int(n) for n in tagid.split(',')]

        match = re.match(r'([\-,/\d]+)([DPIA])', dpnd)
        if match:
            parent = match.group(1)
            self.dpndtype = match.group(2)
            self.parentids = [int(n) for n in parent.split(',')]
        else:
            raise Exception("Illegal synnodes dpnd: %s" % dpnd)

        if string.startswith("<見出し:"):
            end = string.find(">")
            self.midasi = string[5:end]
            self.feature = string[end + 1:]
        else:
            self.feature = string


class SynNode(object):

    def __init__(self, spec):
        self.synid = ''
        self.tagids = []
        self.score = ''
        self.feature = ''

        # ! 1 <SYNID:s1201:所在/しょざい><スコア:0.693><上位語><下位語数:323>
        tagid, string = spec.split(' ')[1:3]
        self.tagids = [int(n) for n in tagid.split(',')]

        match_synid = re.search(r'<SYNID:([^>]+)>', string)
        if match_synid:
            self.synid = match_synid.group(1)
            string = re.sub(r'<SYNID:[^>]+>', '', string)

        if string.startswith("<スコア:"):
            end = string.find(">")
            self.score = float(string[5:end])
            string = string[end + 1:]

        self.feature = string


class SynNodesTest(unittest.TestCase):

    def setUp(self):
        self.str1 = '!! 0 1D <見出し:景気が><格解析結果:ガ格>'
        self.str2 = '!! 0,1 -1D <見出し:冷え込む>'

    def test_synnodes(self):
        synnodes1 = SynNodes(self.str1)
        self.assertIn(0, synnodes1.tagids)
        self.assertIn(1, synnodes1.parentids)
        self.assertEqual(synnodes1.dpndtype, 'D')
        self.assertEqual(synnodes1.midasi, '景気が')
        self.assertEqual(synnodes1.feature, '<格解析結果:ガ格>')

        synnodes2 = SynNodes(self.str2)
        self.assertIn(0, synnodes2.tagids)
        self.assertIn(1, synnodes2.tagids)
        self.assertIn(-1, synnodes2.parentids)
        self.assertEqual(synnodes2.dpndtype, 'D')
        self.assertEqual(synnodes2.midasi, '冷え込む')
        self.assertEqual(synnodes2.feature, '')


class SynNodeTest(unittest.TestCase):

    def setUp(self):
        self.str1 = '! 1 <SYNID:近い/ちかい><スコア:1>'
        self.str2 = '! 1 <SYNID:s199:親しい/したしい><スコア:0.99>'
        self.str3 = '! 1 <SYNID:s1201:所在/しょざい><スコア:0.693><上位語><下位語数:323>'

    def test_synnode(self):
        synnode1 = SynNode(self.str1)
        self.assertEqual(synnode1.synid, '近い/ちかい')
        self.assertIn(1, synnode1.tagids)
        self.assertEqual(synnode1.score, 1)
        self.assertEqual(synnode1.feature, '')

        synnode2 = SynNode(self.str2)
        self.assertEqual(synnode2.synid, 's199:親しい/したしい')
        self.assertEqual(synnode2.score, 0.99)
        self.assertEqual(synnode2.feature, '')

        synnode3 = SynNode(self.str3)
        self.assertEqual(synnode3.synid, 's1201:所在/しょざい')
        self.assertEqual(synnode3.score, 0.693)
        self.assertEqual(synnode3.feature, '<上位語><下位語数:323>')


if __name__ == '__main__':
    unittest.main()
