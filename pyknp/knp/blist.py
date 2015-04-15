#-*- encoding: utf-8 -*-

from pyknp import Bunsetsu
from pyknp import Morpheme
from pyknp import Tag
import re
import sys
import unittest

class BList(object):
    def __init__(self, result_list=[], pattern='EOS'):
        self._bnst = []
        self._readonly = False
        self.comment = ''
        self.pattern = pattern
        self.parse(result_list)
        self.set_parent_child()
    def bnst_id(self):
        match = re.match(r'# S-ID:(.*?)[ $]', self.comment)
        return int(match.group(1))
    def set_bnst_id(self, new_id):
        self.comment = re.sub(r'# S-ID:(.*?)([ $].*)', r'# S-ID:%s\2' % new_id,
                              self.comment)
        return self.bnst_id()
    def parse(self, result_list):
        for string in result_list:
            if string.startswith('#'):
                self.comment = "%s%s" % (self.comment, string)
            elif re.match(self.pattern, string):
                break
            elif string.startswith(';;'):
                sys.stderr.write("Error: %s%s\n" % string)
                quit(1)
            elif string.startswith('*'):
                bnst = Bunsetsu(string, len(self._bnst))
                self._bnst.append(bnst)
            elif string.startswith('+'):
                self._bnst[-1].push_tag(
                        Tag(string, len(self._bnst[-1].tag_list)))
            elif re.match(r'^- (-?\d+)(.+)$', string):
                # TODO(john): what is this?
                pass
            elif string.startswith('!!'):
                # TODO(shibata): SynNodes
                pass
            elif string.startswith('!'):
                # TODO(shibata): SynNodes
                pass
            else:
                mrph = Morpheme(string, len(self._bnst[-1].mrph_list))
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
            for tag in bnst.tag_list:
                result.append(tag)
        return result
    def mrph_list(self):
        result = []
        for bnst in self._bnst:
            for mrph in bnst.mrph_list:
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
        self.result = "# S-ID:123 KNP:4.2-ffabecc DATE:2015/04/10 SCORE:-18.02647\n" \
                "* 1D <BGH:解析/かいせき><文頭><サ変><助詞><連体修飾><体言>\n" \
                "+ 1D <BGH:構文/こうぶん><文節内><係:文節内><文頭><体言>\n" \
                "構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:構文/こうぶん カテゴリ:抽象物\" <代表表記:構文/こうぶん>\n" \
                "+ 2D <BGH:解析/かいせき><助詞><連体修飾><体言>\n" \
                "解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術\" <代表表記:解析/かいせき>\n" \
                "の の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n" \
                "* 2D <BGH:実例/じつれい><ヲ><助詞><体言><係:ヲ格>\n" \
                "+ 3D <BGH:実例/じつれい><ヲ><助詞><体言><係:ヲ格>\n" \
                "実例 じつれい 実例 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:実例/じつれい カテゴリ:抽象物\" <代表表記:実例/じつれい>\n" \
                "を を を 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n" \
                "* -1D <BGH:示す/しめす><文末><句点><用言:動>\n" \
                "+ -1D <BGH:示す/しめす><文末><句点><用言:動>\n" \
                "示す しめす 示す 動詞 2 * 0 子音動詞サ行 5 基本形 2 \"代表表記:示す/しめす\" <代表表記:示す/しめす><正規化代表表記:示す/しめす>\n" \
                "。 。 。 特殊 1 句点 1 * 0 * 0 NIL <英記号><記号><文末><付属>\n" \
                "EOS"
    def test(self):
        blist = BList(self.result.split('\n'))
        self.assertEqual(len(blist), 3)
        self.assertEqual(len(blist.tag_list()), 4)
        self.assertEqual(len(blist.mrph_list()), 7)
        self.assertEqual(''.join([mrph.midasi for mrph in blist.mrph_list()]),
                         '構文解析の実例を示す。')
        self.assertEqual(blist.bnst_id(), 123)
        self.assertEqual(blist.set_bnst_id(234), 234)
        self.assertEqual(blist.bnst_id(), 234)

if __name__ == '__main__':
    unittest.main()
