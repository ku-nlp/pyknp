#-*- encoding: utf-8 -*-

from pyknp import Bunsetsu
from pyknp import Morpheme
from pyknp import Tag
from pyknp import TList
from pyknp import SynNodes, SynNode
from pyknp import DrawTree
import re
import sys
import unittest

class BList(DrawTree):
    """
    文節列を保持するオブジェクト．
    """
    def __init__(self, spec='', pattern='EOS'):
        self._bnst = []
        self._readonly = False
        self.pattern = pattern
        self.comment = ''
        self.sid = ''
        self.parse(spec)
        self.set_parent_child()
    def parse(self, spec):
        for string in spec.split('\n'):
            if string.strip() == "":
                continue
            if string.startswith('#'):
                self.comment = string
                match = re.match(r'# S-ID:(.*?)[ $]', self.comment)
                if match:
                    self.sid = match.group(1)
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
                self._bnst[bnst.parent_id].children.append(bnst)
            for tag in bnst._tag_list:
                if tag.parent_id == -1:
                    tag.parent = None
                else:
                    tag.parent = self.tag_list()[tag.parent_id]
                    self.tag_list()[tag.parent_id].children.append(tag)
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
        return "%s\n%s%s\n" % (self.comment, ''.join(b.spec() for b in self._bnst), self.pattern)
    def all(self):
        return self.spec()
    def __getitem__(self, index):
        return self._bnst[index]
    def __len__(self):
        return len(self._bnst)

    def draw_bnst_tree(self, fh=None):
        """ 文節列の依存関係を木構造として表現して出力する． """
        self.draw_tree(fh=fh)

    def draw_tag_tree(self, fh=None):
        """ タグ列の依存関係を木構造として表現して出力する． """
        tlist = TList()
        for tag in self.tag_list():
            tlist.push_tag(tag)
        tlist.draw_tree(fh=fh)
        
    def draw_tree_leaves(self):
        """ draw_tree メソッドとの通信用のメソッド． """
        return self.bnst_list()
    
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
        self.assertEqual(blist.sid, '123')
        # Check parent/children relations
        self.assertEqual(blist[1].parent, blist[2])
        self.assertEqual(blist[1].parent_id, 2)
        self.assertEqual(blist[2].parent, None)
        self.assertEqual(blist[2].parent_id, -1)
        self.assertEqual(blist[1].children, [blist[0]])
        self.assertEqual(blist[0].children, [])
        self.assertEqual(blist.tag_list()[1].parent, blist.tag_list()[2])
        self.assertEqual(blist.tag_list()[2].children, [blist.tag_list()[1]])

if __name__ == '__main__':
    unittest.main()
