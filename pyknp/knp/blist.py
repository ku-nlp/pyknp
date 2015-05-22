#-*- encoding: utf-8 -*-

from pyknp import Bunsetsu
from pyknp import Morpheme
from pyknp import Tag
from pyknp import SynNodes, SynNode
import re
import sys
import unittest

class BList(object):
    """
    文節列を保持するオブジェクト．
    """
    def __init__(self, spec='', pattern='EOS'):
        self._bnst = []
        self._readonly = False
        self.comment = ''
        self.pattern = pattern
        self.parse(spec)
        self.set_parent_child()
    def sid(self):
        match = re.match(r'# S-ID:(.*?)[ $]', self.comment)
        return int(match.group(1))
    def set_sid(self, new_id):
        self.comment = re.sub(r'# S-ID:(.*?)([ $].*)', r'# S-ID:%s\2' % new_id,
                              self.comment)
        return self.sid()
    def parse(self, spec):
        for string in spec.split('\n'):
            if string.strip() == "":
                continue
            if string.startswith('#'):
                self.comment = "%s%s" % (self.comment, string)
            elif re.match(self.pattern, string):
                break
            elif string.startswith(';;'):
                sys.stderr.write("Error: %s\n" % string)
                quit(1)
            elif string.startswith('*'):
                bnst = Bunsetsu(string, len(self._bnst))
                self._bnst.append(bnst)
            elif string.startswith('+'):
                self._bnst[-1].push_tag(
                        Tag(string, len(self.tag_list())))
            elif re.match(r'^- (-?\d+)(.+)$', string):
                # TODO(john): what is this?
                pass
            elif string.startswith('!!'):
                synnodes = SynNodes(string)
                self._bnst[-1].tag_list().push_synnodes(synnodes)
            elif string.startswith('!'):
                synnode = SynNode(string)
                self._bnst[-1].tag_list().push_synnode(synnode)
            elif string.startswith('EOS'):
                pass
            else:
                mrph = Morpheme(string, len(self.mrph_list()))
                self._bnst[-1].push_mrph(mrph)
    def set_parent_child(self):
        for bnst in self._bnst:
            if bnst.parent_id == -1:
                bnst.parent = None
            else:
                bnst.parent = self._bnst[bnst.parent_id]
                self._bnst[bnst.parent_id].child.append(bnst)
    def push_bnst(self, bnst):
        self._bnst.append(bnst)
        self._bnst[bnst.parent].child.append(bnst.bnst_id)
    def tag_list(self):
        result = []
        for bnst in self._bnst:
            for tag in bnst.tag_list():
                result.append(tag)
        return result
    def mrph_list(self):
        result = []
        for bnst in self._bnst:
            for mrph in bnst.mrph_list():
                result.append(mrph)
        return result
    def bnst_list(self):
        return self._bnst
    def set_readonly(self):
        for bnst in self._bnst:
            bnst.set_readonly()
        self._readonly = True
    def spec(self):
        return "%s%s" % (self.comment, ''.join(b.spec for b in self._bnst))
    def __getitem__(self, index):
        return self._bnst[index]
    def __len__(self):
        return len(self._bnst)

class BListTest(unittest.TestCase):
    def setUp(self):
        self.result = u"# S-ID:123 KNP:4.2-ffabecc DATE:2015/04/10 SCORE:-18.02647\n" \
                u"* 1D <BGH:解析/かいせき><文頭><サ変><助詞><連体修飾><体言>\n" \
                u"+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>\n" \
                u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>\n" \
                u"+ 2D <BGH:解析/かいせき><助詞><連体修飾><体言>\n" \
                u"解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術\" <代表表記:解析/かいせき>\n" \
                u"の の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n" \
                u"* 2D <BGH:実例/じつれい><ヲ><助詞><体言><係:ヲ格>\n" \
                u"+ 3D <BGH:実例/じつれい><ヲ><助詞><体言><係:ヲ格>\n" \
                u"実例 じつれい 実例 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:実例/じつれい カテゴリ:抽象物\" <代表表記:実例/じつれい>\n" \
                u"を を を 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n" \
                u"* -1D <BGH:示す/しめす><文末><句点><用言:動>\n" \
                u"+ -1D <BGH:示す/しめす><文末><句点><用言:動>\n" \
                u"示す しめす 示す 動詞 2 * 0 子音動詞サ行 5 基本形 2 \"代表表記:示す/しめす\" <代表表記:示す/しめす><正規化代表表記:示す/しめす>\n" \
                u"。 。 。 特殊 1 句点 1 * 0 * 0 NIL <英記号><記号><文末><付属>\n" \
                u"EOS"
    def test(self):
        blist = BList(self.result)
        self.assertEqual(len(blist), 3)
        self.assertEqual(len(blist.tag_list()), 4)
        self.assertEqual(len(blist.mrph_list()), 7)
        self.assertEqual(''.join([mrph.midasi for mrph in blist.mrph_list()]),
                         u'構文解析の実例を示す。')
        self.assertEqual(blist.sid(), 123)
        self.assertEqual(blist.set_sid(234), 234)
        self.assertEqual(blist.sid(), 234)

if __name__ == '__main__':
    unittest.main()
