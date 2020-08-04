# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from pyknp import Argument, Pas
from pyknp import Bunsetsu
from pyknp import Morpheme, JUMAN_FORMAT
from pyknp import Tag
from pyknp import TList
from pyknp import SynNodes, SynNode
from pyknp import draw_tree, sprint_tree
import re
import unittest
import json
import bisect


class BList(object):
    """ ある文に関する文節列を保持するオブジェクト

    Args:
        spec (str): KNP出力
        pattern (str): KNP出力の終端記号
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

    Attributes:
        comment (str): KNP出力における、#から始まる行に書かれた文字列
        sid (str): 文ID (KNP出力中のS-ID)
    """

    def __init__(self, spec='', pattern='EOS', juman_format=JUMAN_FORMAT.DEFAULT):
        self._bnst = []
        self._readonly = False
        self.pattern = pattern
        self.juman_format = juman_format
        self.comment = ''
        self.sid = ''
        self._pinfos = []
        self.parse(spec)
        self._set_parent_child()
        self._set_positions()
        self._set_pas(self.juman_format)
        # set midasi
        for i in range(len(self._bnst)):
            self._bnst[i].set_midasi()

    def _set_pas(self, juman_format):
        """ 各基本句にPASを設定 """
        tag_list = self.tag_list()
        if juman_format != JUMAN_FORMAT.DEFAULT:
            for pinfo in self._pinfos:
                pinfo = json.loads(pinfo)

                tag_idx = pinfo.get("tid")
                if tag_idx is None:
                    end = pinfo["head_token_end"]
                    tag_idx = bisect.bisect(self.tag_positions, end) - 1

                tag = tag_list[tag_idx]
                tag.pas = Pas()
                tag.pas.cfid = pinfo["cfid"]

                for casename, args in pinfo["args"].items():
                    for arg in args:
                        arg_tag_idx = arg.get("tid")
                        if arg_tag_idx is None:
                            arg_tag_idx = bisect.bisect(self.tag_positions, arg["head_token_end"]) - 1
                        arg_sid = arg.get("sid")
                        if (arg_sid is None) or (len(arg["sid"]) == 0):
                            arg_sid = self.sid

                        arg = Argument(sid=arg_sid, tid=arg_tag_idx, midasi=arg["rep"])
                        tag.pas.arguments[casename].append(arg)
        else:
            # KNPの述語項構造をparse
            for tag in tag_list:
                if ("格解析結果" in tag.features) or ("述語項構造" in tag.features):
                    tag.pas = Pas(tag.tag_id, self)

    def parse(self, spec):
        """ KNPの出力を読み取る 

        Args:
            spec (str): KNP出力
        """
        for string in spec.split('\n'):
            if string.strip() == "":
                continue
            if string.startswith('#\t'):
                items = string.split("\t")
                if len(items) >= 3 and items[1] == "PAS":
                    self._pinfos.append(items[2])
            elif string.startswith('#'):
                if self.comment:
                    self.comment += "\n"
                self.comment += string
                match = re.match(r'# S-ID: ?(\S*)( .+)?$', self.comment)
                if match:
                    self.sid = match.group(1)
                if 'KNP++' in string and 'output:KNP' not in string:
                    self.juman_format = JUMAN_FORMAT.LATTICE_TOP_ONE  # TODO
            elif re.match(self.pattern, string):
                break
            elif string.startswith(';;'):
                raise Exception("Error: %s" % string)
            elif string.startswith('*'):
                bnst = Bunsetsu(string, len(self._bnst))
                self._bnst.append(bnst)
            elif string.startswith('+'):
                if self.juman_format != JUMAN_FORMAT.DEFAULT:  # TODO
                    bnst = Bunsetsu(string, len(self._bnst), self.juman_format)
                    self._bnst.append(bnst)
                self._bnst[-1].push_tag(
                    Tag(string, len(self.tag_list()), self.juman_format))
            elif string.startswith('!!'):
                synnodes = SynNodes(string)
                self._bnst[-1].tag_list().push_synnodes(synnodes)
            elif string.startswith('!') and not string.startswith('! ! !'):
                synnode = SynNode(string)
                self._bnst[-1].tag_list().push_synnode(synnode)
            elif string.startswith('EOS'):
                pass
            else:
                mrph = Morpheme(string, len(self.mrph_list()), self.juman_format)
                if len(self._bnst) == 0:
                    bnst = Bunsetsu("*", len(self._bnst))
                    self._bnst.append(bnst)
                self._bnst[-1].push_mrph(mrph)

    def _set_positions(self):
        mrphs = self.mrph_list()
        if len(mrphs) == 0:
            return
        begin_position = mrphs[0].span[0] 
        
        self.mrph_positions = [begin_position]
        self.tag_positions = [begin_position]
        for mrph in self.mrph_list():
            self.mrph_positions.append(self.mrph_positions[-1] + len(mrph.midasi))
        for tag in self.tag_list():
            start_mrph_index = tag.mrph_list()[0].mrph_index
            end_mrph_index = tag.mrph_list()[-1].mrph_index
            length = self.mrph_positions[end_mrph_index + 1] - self.mrph_positions[start_mrph_index]
            self.tag_positions.append(self.tag_positions[-1] + length)

    def get_tag_span(self, tag_id):
        """ 基本句の位置情報を返す

        Args:
            tag_id (int): 基本句ID

        Returns:
            tuple: (基本句の開始位置, 終了位置)
        """
        return self.tag_positions[tag_id], self.tag_positions[tag_id + 1] - 1

    def _set_parent_child(self):
        for bnst in self._bnst:
            if bnst.parent_id == -1:
                bnst.parent = None
            else:
                bnst.parent = self._bnst[bnst.parent_id]
                self._bnst[bnst.parent_id].children.append(bnst)
            for tag in bnst.tag_list():
                if tag.parent_id == -1:
                    tag.parent = None
                else:
                    tag.parent = self.tag_list()[tag.parent_id]
                    tag.parent.children.append(tag)

    def push_bnst(self, bnst):
        self._bnst.append(bnst)
        self._bnst[bnst.parent].child.append(bnst.bnst_id)

    def tag_list(self):
        """ 文を構成する全基本句オブジェクトを返す

        Returns:
            list of Tag: 基本句オブジェクトTagのリスト
        """
        return [tag for bnst in self._bnst for tag in bnst.tag_list()]

    def mrph_list(self):
        """ 文を構成する全形態素オブジェクトを返す

        Returns:
            list of Morpheme: 形態素オブジェクトMorphemeのリスト
        """
        return [mrph for bnst in self._bnst for mrph in bnst.mrph_list()]

    def bnst_list(self):
        """ 文を構成する全文節オブジェクトを返す 

        Returns:
            list of Bunsetsu: 文節オブジェクトBunsetsuのリスト
        """
        return self._bnst

    def set_readonly(self):
        for bnst in self._bnst:
            bnst.set_readonly()
        self._readonly = True

    def spec(self):
        return "%s\n%s%s\n" % (self.comment, ''.join(b.spec() for b in self._bnst), self.pattern)

    def all(self):
        """ KNPの出力結果を返す """
        return self.spec()

    def __getitem__(self, index):
        return self._bnst[index]

    def __len__(self):
        return len(self._bnst)

    def draw_tree(self, fh=None, show_pos=True):
        self.draw_bnst_tree(fh=fh, show_pos=show_pos)

    def draw_bnst_tree(self, fh=None, show_pos=True):
        """ 文節列の依存関係を木構造として表現して出力する． """
        draw_tree(self._bnst, fh=fh, show_pos=show_pos)

    def draw_tag_tree(self, fh=None, show_pos=True):
        """ タグ列の依存関係を木構造として表現して出力する． """
        tlist = TList()
        for tag in self.tag_list():
            tlist.push_tag(tag)
        tlist.draw_tree(fh=fh, show_pos=show_pos)

    def sprint_tree(self, show_pos=True):
        return sprint_tree(self._bnst, show_pos=show_pos)

    def get_clause_starts(self, concat_clause_in_paren=False, discourse_clause=False):
        """ 節の冒頭句の位置情報を返す

        Args:
            concat_clause_in_paren (bool):  括弧内では節を切らないかどうか
            discourse_clause (bool): 補文節、連体修飾節を切らないかどうか

        Returns:
            list: 節の冒頭となる基本句idのリスト
        """
        starts = [0]
        paren_level = 0
        tags = self.tag_list()
        for idx, tag in enumerate(tags):
            features = tag.features  # alias

            if features.get("括弧始"):
                paren_level += 1
            elif features.get("括弧終"):
                paren_level -= 1

            if (not concat_clause_in_paren or paren_level == 0) and idx != len(tags) - 1:
                if features.get("節-区切"):
                    if discourse_clause is True and (features.get("節-区切") == "連体修飾" or features.get("節-区切") == "補文"):
                        continue
                    else:
                        starts.append(idx + 1)
        return starts


class BListTest(unittest.TestCase):

    def setUp(self):
        pass

    def test1(self):
        result = "# S-ID:123 KNP:4.2-ffabecc DATE:2015/04/10 SCORE:-18.02647\n" \
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

        blist = BList(result)
        self.assertEqual(len(blist), 3)
        self.assertEqual(len(blist.tag_list()), 4)
        self.assertEqual(len(blist.mrph_list()), 7)
        self.assertEqual(''.join([mrph.midasi for mrph in blist.mrph_list()]),
                         '構文解析の実例を示す。')
        self.assertEqual(blist.sid, '123')
        self.assertEqual(blist.all(), result + "\n")
        # Check parent/children relations
        self.assertEqual(blist[1].parent, blist[2])
        self.assertEqual(blist[1].parent_id, 2)
        self.assertEqual(blist[2].parent, None)
        self.assertEqual(blist[2].parent_id, -1)
        self.assertEqual(blist[1].children, [blist[0]])
        self.assertEqual(blist[0].children, [])
        self.assertEqual(blist.tag_list()[1].parent, blist.tag_list()[2])
        self.assertEqual(blist.tag_list()[2].children, [blist.tag_list()[1]])
        self.assertEqual(blist.mrph_positions, [0, 2, 4, 5, 7, 8, 10, 11])
        self.assertEqual(blist.tag_positions, [0, 2, 5, 8, 11])
        spans = [(0, 1), (2, 4), (5, 7), (8, 10)]
        for i, t in enumerate(blist.tag_list()):
            self.assertEqual(blist.get_tag_span(t.tag_id), spans[i])

    def test2(self):
        result = """# S-ID:foo KNP++:a9af601
+	0	3	D	1;3	母が	母/ぼ	-	-	-	-	-	-	-	-	-	-	BP:Phrase|CFG_RULE_ID:1|BOS|BP_TYPE|ガ|助詞
-	1	0	0	0	母	母/ぼ	ぼ	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:音|漢字|CONT|RelWord-105522
-	3	1;2	1	1	が	*	が	が	助詞	9	接続助詞	3	*	0	*	0	FUNC|Ｔ固有付属|Ｔ固有任意
+	1	3	D	5;6	姉に	姉/あね	-	-	-	-	-	-	-	-	-	-	BP:Phrase|CFG_RULE_ID:1|BP_TYPE|ニ|助詞|体言
-	5	3;4	2	2	姉	姉/あね	あね	姉	名詞	6	普通名詞	1	*	0	*	0	漢字読み:訓|カテゴリ:人|漢字|CONT|LD
-	6	5	3	3	に	*	に	に	助詞	9	接続助詞	3	*	0	*	0	FUNC|Ｔ固有付属|Ｔ固有任意
+	2	3	D	8;9	弁当を	弁当/べんとう	-	-	-	-	-	-	-	-	-	-	BP:Phrase|CFG_RULE_ID:1|BP_TYPE|ヲ
-	8	6;7	4	5	弁当	弁当/べんとう	べんとう	弁当	名詞	6	普通名詞	1	*	0	*	0	カテゴリ:人工物-食べ
-	9	8	6	6	を	*	を	を	助詞	9	格助詞	1	*	0	*	0	FUNC|Ｔ固有付属|Ｔ固有任意
+	3	-1	D	10	渡した	渡す/わたす	-	-	-	-	-	-	-	-	-	-	EOS|BP:Phrase|CFG_RULE_ID:0|BP_TYPE
-	10	9	7	9	渡した	渡す/わたす	わたした	渡す	動詞	2	*	0	子音動詞サ行	5	タ形	10	付属動詞候補（基本）
#	PAS	{"predtype" : "PRED", "sid":"", "token_start":7, "token_end":9, "rep":"渡す/わたす", "head_token_start":7, "head_token_end":9, "cfid" : "渡す/わたす:動1", "score" : -27.2318, "args" : {"ヲ" : [{"sid":"", "token_start":4, "token_end":6, "rep":"弁当/べんとう", "head_token_start":4, "head_token_end":6}], "ガ" : [{"sid":"", "token_start":0, "token_end":1, "rep":"母/ぼ", "head_token_start":0, "head_token_end":1}], "ニ" : [{"sid":"", "token_start":2, "token_end":3, "rep":"姉/あね", "head_token_start":2, "head_token_end":3}]}}
EOS"""

        blist = BList(result, juman_format=JUMAN_FORMAT.LATTICE_TOP_ONE)
        self.assertEqual(len(blist), 4)
        self.assertEqual(len(blist.tag_list()), 4)
        self.assertEqual(len(blist.mrph_list()), 7)
        self.assertEqual(''.join([mrph.midasi for mrph in blist.mrph_list()]),
                         '母が姉に弁当を渡した')
        self.assertEqual(blist.sid, 'foo')
        self.assertEqual(blist[1].parent, blist[3])
        self.assertEqual(blist[1].parent_id, 3)
        self.assertEqual(blist[3].parent, None)
        self.assertEqual(blist[3].parent_id, -1)
        self.assertEqual(blist[0].children, [])
        self.assertEqual(blist[1].children, [])
        self.assertEqual(blist[3].children, [blist[0], blist[1], blist[2]])

        self.assertEqual(blist.tag_list()[1].parent, blist.tag_list()[3])
        self.assertEqual(blist.tag_list()[3].children, [blist.tag_list()[0], blist.tag_list()[1], blist.tag_list()[2]])
        self.assertEqual(blist.mrph_positions, [0, 1, 2, 3, 4, 6, 7, 10])
        self.assertEqual(blist.tag_positions, [0, 2, 4, 7, 10])
        spans = [(0, 1), (2, 3), (4, 6), (7, 9)]
        tags = blist.tag_list()
        for i, t in enumerate(tags):
            self.assertEqual(blist.get_tag_span(t.tag_id), spans[i])
        self.assertEqual(blist.get_clause_starts(), [0])

        self.assertEqual(tags[0].pas, None)
        self.assertEqual(tags[1].pas, None)
        self.assertEqual(tags[2].pas, None)
        self.assertEqual(tags[3].pas.cfid, "渡す/わたす:動1")
        self.assertEqual(tags[3].features.pas.cfid, "渡す/わたす:動1")
        args = tags[3].pas.arguments
        self.assertEqual(len(args), 3)
        self.assertEqual(len(args["ヲ"]), 1)
        self.assertEqual(args["ヲ"][0].sid, "foo")
        self.assertEqual(args["ヲ"][0].tid, 2)


class PasTest41(unittest.TestCase):  # KNP v4.19

    def setUp(self):
        pass

    def test(self):
        spec = """
# S-ID:1 KNP:4.19-CF1.1 DATE:2018/10/19 SCORE:-22.05720
* 4D <文頭><SM-主体><SM-人><ハ><助詞><体言><一文字漢字><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:彼/かれ><主辞代表表記:彼/かれ>
+ 4D <文頭><SM-主体><SM-人><ハ><助詞><体言><一文字漢字><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><人称代名詞><正規化代表表記:彼/かれ><照応詞候補:彼><解析格:ガ><EID:0>
彼 かれ 彼 名詞 6 普通名詞 1 * 0 * 0 "代表表記:彼/かれ 漢字読み:訓 カテゴリ:人" <代表表記:彼/かれ><漢字読み:訓><カテゴリ:人><正規化代表表記:彼/かれ><文頭><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
は は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* 2D <ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><正規化代表表記:御飯/ごはん><主辞代表表記:御飯/ごはん>
+ 2D <ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:御飯/ごはん><照応詞候補:ご飯><解析格:ヲ><EID:1>
ご飯 ごはん ご飯 名詞 6 普通名詞 1 * 0 * 0 "代表表記:御飯/ごはん カテゴリ:人工物-食べ物 ドメイン:料理・食事" <代表表記:御飯/ごはん><カテゴリ:人工物-食べ物><ドメイン:料理・食事><正規化代表表記:御飯/ごはん><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
を を を 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* 4P <用言:動><係:連用><レベル:B><並キ:述:&レベル:強><区切:3-5><ID:動詞連用><連用要素><連用節><動態述語><正規化代表表記:食べる/たべる><主辞代表表記:食べる/たべる><並列類似度:1.587><並結句数:2><並結文節数:2><提題受:30>
+ 4P <用言:動><係:連用><レベル:B><並キ:述:&レベル:強><区切:3-5><ID:動詞連用><連用要素><連用節><動態述語><正規化代表表記:食べる/たべる><用言代表表記:食べる/たべる><提題受:30><格関係1:ヲ:ご飯><格解析結果:食べる/たべる:動1:ガ/U/-/-/-/-;ヲ/C/ご飯/1/0/1;ニ/U/-/-/-/-;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;修飾/U/-/-/-/-;ノ/U/-/-/-/-;トスル/U/-/-/-/-;ニヨル/U/-/-/-/-;ニツク/U/-/-/-/-;トイウ/U/-/-/-/-;ニナラブ/U/-/-/-/-;ニツヅク/U/-/-/-/-;ニアワセル/U/-/-/-/-><EID:2><項構造:食べる/たべる:動1:ヲ/C/ご飯/1;ガ/N/彼/0>
食べ たべ 食べる 動詞 2 * 0 母音動詞 1 基本連用形 8 "代表表記:食べる/たべる ドメイン:料理・食事" <代表表記:食べる/たべる><ドメイン:料理・食事><正規化代表表記:食べる/たべる><かな漢字><活用語><連用形名詞化疑><自立><内容語><タグ単位始><文節始><文節主辞>
* 4D <ヘ><助詞><体言><係:ヘ格><区切:0-0><格要素><連用要素><正規化代表表記:大学/だいがく><主辞代表表記:大学/だいがく>
+ 4D <ヘ><助詞><体言><係:ヘ格><区切:0-0><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:大学/だいがく><照応詞候補:大学><解析格:ヘ><EID:3><項構造:大学/だいがく:名0>
大学 だいがく 大学 名詞 6 普通名詞 1 * 0 * 0 "代表表記:大学/だいがく 組織名末尾 カテゴリ:場所-施設 ドメイン:教育・学習" <代表表記:大学/だいがく><組織名末尾><カテゴリ:場所-施設><ドメイン:教育・学習><正規化代表表記:大学/だいがく><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
へ へ へ 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* -1D <文末><時制-過去><用言:動><レベル:C><区切:5-5><ID:（文末）><提題受:30><主節><動態述語><正規化代表表記:行く/いく?行う/おこなう><主辞代表表記:行く/いく?行う/おこなう>
+ -1D <文末><時制-過去><用言:動><レベル:C><区切:5-5><ID:（文末）><提題受:30><主節><動態述語><正規化代表表記:行く/いく?行う/おこなう><用言代表表記:行く/いく?行う/おこなう><主題格:一人称優位><格関係0:ガ:彼><格関係3:ヘ:大学><格解析結果:行く/いく:動1:ガ/N/彼/0/0/1;ヲ/U/-/-/-/-;ニ/U/-/-/-/-;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/C/大学/3/0/1;時間/U/-/-/-/-;外の関係/U/-/-/-/-;修飾/U/-/-/-/-;ノ/U/-/-/-/-;トスル/U/-/-/-/-;ニツク/U/-/-/-/-;トイウ/U/-/-/-/-;ニカギル/U/-/-/-/-;ニヨル/U/-/-/-/-;ニアワセル/U/-/-/-/-><EID:4><項構造:行く/いく:動1:ヘ/C/大学/3;ガ/N/彼/0>
行った いった 行く 動詞 2 * 0 子音動詞カ行促音便形 3 タ形 10 "代表表記:行く/いく 付属動詞候補（タ系） ドメイン:交通 反義:動詞:帰る/かえる" <代表表記:行く/いく><付属動詞候補（タ系）><ドメイン:交通><反義:動詞:帰る/かえる><正規化代表表記:行く/いく?行う/おこなう><品曖><ALT-行った-おこなった-行う-2-0-12-10-"代表表記:行う/おこなう"><品曖-動詞><原形曖昧><文末><表現文末><移動動詞><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞><用言曖昧性解消>
EOS
"""
        # <項構造:行く/いく:動1:ヘ/C/大学/3;ガ/N/彼/0>
        pas = Pas(tid=4, result=BList(spec))

        self.assertEqual(pas.cfid, "行く/いく:動1")

        self.assertEqual(pas.eid2tid, {0: 0, 1: 1, 2: 2, 3: 3, 4: 4})

        self.assertEqual(pas.arguments["ガ"][0].sid, "1")
        self.assertEqual(pas.arguments["ガ"][0].tid, 0)
        self.assertEqual(pas.arguments["ガ"][0].eid, 0)
        self.assertEqual(pas.arguments["ガ"][0].midasi, "彼")
        self.assertEqual(pas.arguments["ガ"][0].flag, "N")
        self.assertEqual(pas.arguments["ガ"][0].sdist, 0)


class PasTest42(unittest.TestCase):  # KNP v4.20

    def setUp(self):
        pass

    def test1(self):
        spec = """
# S-ID:1 KNP:4.2-a01607a1 DATE:2018/10/19 SCORE:-25.47925
* 4D <SM-主体><SM-人><BGH:彼/かれ><文頭><ハ><助詞><体言><一文字漢字><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:彼/かれ><主辞代表表記:彼/かれ>
+ 4D <SM-主体><SM-人><BGH:彼/かれ><文頭><ハ><助詞><体言><一文字漢字><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><人称代名詞><正規化代表表記:彼/かれ><主辞代表表記:彼/かれ><照応詞候補:彼><解析格:ガ><EID:5>
彼 かれ 彼 名詞 6 普通名詞 1 * 0 * 0 "代表表記:彼/かれ 漢字読み:訓 カテゴリ:人" <代表表記:彼/かれ><漢字読み:訓><カテゴリ:人><正規化代表表記:彼/かれ><漢字><かな漢字><名詞相当語><文頭><自立><内容語><タグ単位始><文節始><文節主辞>
は は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* 2D <BGH:御飯/ごはん><ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><正規化代表表記:御飯/ごはん><主辞代表表記:御飯/ごはん>
+ 2D <BGH:御飯/ごはん><ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:御飯/ごはん><主辞代表表記:御飯/ごはん><照応詞候補:ご飯><解析格:ヲ><EID:6>
ご飯 ごはん ご飯 名詞 6 普通名詞 1 * 0 * 0 "代表表記:御飯/ごはん カテゴリ:人工物-食べ物 ドメイン:料理・食事" <代表表記:御飯/ごはん><カテゴリ:人工物-食べ物><ドメイン:料理・食事><正規化代表表記:御飯/ごはん><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
を を を 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* 4P <BGH:食べる/たべる><用言:動><係:連用><レベル:B><並キ:述:&レベル:強><区切:3-5><ID:動詞連用><連用要素><連用節><動態述語><正規化代表表記:食べる/たべる><主辞代表表記:食べる/たべる><並列類似度:1.587><並結句数:2><並結文節数:2><提題受:30>
+ 4P <BGH:食べる/たべる><用言:動><係:連用><レベル:B><並キ:述:&レベル:強><区切:3-5><ID:動詞連用><連用要素><連用節><動態述語><正規化代表表記:食べる/たべる><主辞代表表記:食べる/たべる><用言代表表記:食べる/たべる><提題受:30><節-区切><節-主辞><格関係1:ヲ:ご飯><標準用言代表表記:食べる/たべる><EID:7><述語項構造:食べる/たべる:動1:ガ/N/彼/0/0/5;ヲ/C/ご飯/0/1/6;ニ/E/著者/2/-1/0;ト/-/-/-/-/-;デ/-/-/-/-/-;カラ/-/-/-/-/-;ヨリ/-/-/-/-/-;マデ/-/-/-/-/-;ヘ/-/-/-/-/-;時間/-/-/-/-/-;外の関係/-/-/-/-/-;修飾/-/-/-/-/-><省略解析信頼度:0.253><ガ格省略解析信頼度:0.000>
食べ たべ 食べる 動詞 2 * 0 母音動詞 1 基本連用形 8 "代表表記:食べる/たべる ドメイン:料理・食事" <代表表記:食べる/たべる><ドメイン:料理・食事><正規化代表表記:食べる/たべる><かな漢字><活用語><連用形名詞化疑><自立><内容語><タグ単位始><文節始><文節主辞><用言表記末尾>
* 4D <SM-主体><SM-場所><SM-組織><BGH:大学/だいがく><ヘ><助詞><体言><係:ヘ格><区切:0-0><格要素><連用要素><正規化代表表記:大学/だいがく><主辞代表表記:大学/だいがく>
+ 4D <SM-主体><SM-場所><SM-組織><BGH:大学/だいがく><ヘ><助詞><体言><係:ヘ格><区切:0-0><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:大学/だいがく><主辞代表表記:大学/だいがく><照応詞候補:大学><解析格:ヘ><EID:8>
大学 だいがく 大学 名詞 6 普通名詞 1 * 0 * 0 "代表表記:大学/だいがく 組織名末尾 カテゴリ:場所-施設 ドメイン:教育・学習" <代表表記:大学/だいがく><組織名末尾><カテゴリ:場所-施設><ドメイン:教育・学習><正規化代表表記:大学/だいがく><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
へ へ へ 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>
* -1D <BGH:行く/いく><文末><時制-過去><句点><用言:動><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><動態述語><正規化代表表記:行く/いく><主辞代表表記:行く/いく>
+ -1D <BGH:行く/いく><文末><時制-過去><句点><用言:動><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><動態述語><正規化代表表記:行く/いく><主辞代表表記:行く/いく><用言代表表記:行く/いく><節-区切><節-主辞><主題格:一人称優位><格関係0:ガ:彼><格関係3:ヘ:大学><標準用言代表表記:行く/いく><EID:9><述語項構造:行く/いく:動12:ガ/N/彼/0/0/5;ニ/E/著者/2/-1/0;ト/-/-/-/-/-;デ/-/-/-/-/-;カラ/-/-/-/-/-;ヨリ/-/-/-/-/-;マデ/-/-/-/-/-;ヘ/C/大学/0/3/8;時間/-/-/-/-/-;外の関係/-/-/-/-/-;修飾/-/-/-/-/-;ノ/-/-/-/-/-><省略解析信頼度:0.777><ガ格省略解析信頼度:0.000>
行った いった 行く 動詞 2 * 0 子音動詞カ行促音便形 3 タ形 10 "代表表記:行く/いく 付属動詞候補（タ系） ドメイン:交通 反義:動詞:帰る/かえる" <代表表記:行く/いく><付属動詞候補（タ系）><ドメイン:交通><反義:動詞:帰る/かえる><正規化代表表記:行く/いく><移動動詞><かな漢字><活用語><表現文末><自立><内容語><タグ単位始><文節始><文節主辞><用言表記末尾>
。 。 。 特殊 1 句点 1 * 0 * 0 NIL <英記号><記号><文末><付属>
EOS
"""
        # <EID:7><述語項構造:食べる/たべる:動1:ガ/N/彼/0/0/5;ヲ/C/ご飯/0/1/6;ニ/E/著者/2/-1/0;ト/-/-/-/-/-;デ/-/-/-/-/-;カラ/-/-/-/-/-;ヨリ/-/-/-/-/-;マデ/-/-/-/-/-;ヘ/-/-/-/-/-;時間/-/-/-/-/-;外の関係/-/-/-/-/-;修飾/-/-/-/-/->
        pas = Pas(tid=4, result=BList(spec))

        self.assertEqual(pas.cfid, "行く/いく:動12")

        self.assertEqual(pas.arguments["ガ"][0].sid, "1")
        self.assertEqual(pas.arguments["ガ"][0].tid, 0)
        self.assertEqual(pas.arguments["ガ"][0].eid, 5)
        self.assertEqual(pas.arguments["ガ"][0].midasi, "彼")
        self.assertEqual(pas.arguments["ガ"][0].flag, "N")
        self.assertEqual(pas.arguments["ガ"][0].sdist, 0)

    def test2(self):
        spec = """
# S-ID:1 KNP:4.20-CF1.1 DATE:2020/08/04 SCORE:-41.95960
* 1D <文頭><感動詞><修飾><係:連用><区切:0-4><連用要素><連用節><正規化代表表記:こんにちは/こんにちは><主辞代表表記:こんにちは/こんにちは>
+ 1D <文頭><感動詞><修飾><係:連用><区切:0-4><連用要素><連用節><正規化代表表記:こんにちは/こんにちは>
こんにちは こんにちは こんにちは 感動詞 12 * 0 * 0 * 0 "代表表記:こんにちは/こんにちは" <代表表記:こんにちは/こんにちは><正規化代表表記:こんにちは/こんにちは><文頭><かな漢字><ひらがな><自立><内容語><タグ単位始><文節始><文節主辞>
* -1D <文末><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><状態述語><正規化代表表記::/:><主辞代表表記::/:>
+ -1D <文末><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><状態述語><判定詞><名詞項候補><先行詞候補><正規化代表表記::/:><用言代表表記::/:><時制-無時制><格解析結果::/::判0:ガ/U/-/-/-/->
: : : 名詞 6 普通名詞 1 * 0 * 0 "未知語:未対応文字種 品詞推定:特殊 疑似代表表記 代表表記::/: 品詞変更::-:-:-15-1-0-0" <未知語><品詞推定:特殊><疑似代表表記><代表表記::/:><正規化代表表記::/:><文末><表現文末><品詞変更::-:-:-15-1-0-0-"未知語:未対応文字種 品詞推定:特殊 疑似代表表記 代表表記::/:"><品曖-その他><記英数カ><英記号><記号><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
EOS
"""
        # <格解析結果::/::判0:ガ/U/-/-/-/->
        pas = Pas(tid=1, result=BList(spec))

        self.assertEqual(pas.cfid, ":/::判0")

    def test3(self):
        spec = """
# S-ID:1 KNP:4.20-CF1.1 DATE:2020/08/03 SCORE:-45.92298
* 1D <文頭><サ変><サ変動詞><連体修飾><用言:動><係:連格><レベル:B><区切:0-5><ID:（動詞連体）><連体節><動態述語><正規化代表表記:表示/ひょうじ><主辞代表表記:表示/ひょうじ>
+ 1D <文頭><サ変動詞><連体修飾><用言:動><係:連格><レベル:B><区切:0-5><ID:（動詞連体）><連体節><動態述語><サ変><正規化代表表記:表示/ひょうじ><用言代表表記:表示/ひょうじ><時制-未来><格関係1:ガ:;><格解析結果:表示/ひょうじ:動2:ガ/N/;/1/0/1;ヲ/U/-/-/-/-;ニ/U/-/-/-/-;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;修飾/U/-/-/-/-;ニヨル/U/-/-/-/-;トスル/U/-/-/-/-;ニツク/U/-/-/-/-;ニモトヅク/U/-/-/-/-;ニアワセル/U/-/-/-/-;ニタイスル/U/-/-/-/-;ニオク/U/-/-/-/->
表示 ひょうじ 表示 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:表示/ひょうじ カテゴリ:抽象物" <代表表記:表示/ひょうじ><カテゴリ:抽象物><正規化代表表記:表示/ひょうじ><文頭><漢字><かな漢字><名詞相当語><サ変><サ変動詞><自立><内容語><タグ単位始><文節始><文節主辞>
する する する 動詞 2 * 0 サ変動詞 16 基本形 2 "代表表記:する/する 自他動詞:自:成る/なる 付属動詞候補（基本）" <代表表記:する/する><自他動詞:自:成る/なる><付属動詞候補（基本）><正規化代表表記:する/する><とタ系連用テ形複合辞><かな漢字><ひらがな><活用語><付属>
* -1D <文末><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><状態述語><正規化代表表記:;/;><主辞代表表記:;/;>
+ -1D <文末><体言><用言:判><体言止><レベル:C><区切:5-5><ID:（文末）><裸名詞><提題受:30><主節><状態述語><判定詞><名詞項候補><先行詞候補><正規化代表表記:;/;><用言代表表記:;/;><時制-無時制><解析連格:ガ><格解析結果:;/;:判0:ガ/U/-/-/-/->
; ; ; 名詞 6 普通名詞 1 * 0 * 0 "未知語:その他 品詞推定:特殊 疑似代表表記 代表表記:;/; 品詞変更:;-;-;-15-1-0-0" <未知語><品詞推定:特殊><疑似代表表記><代表表記:;/;><正規化代表表記:;/;><文末><表現文末><品詞変更:;-;-;-15-1-0-0-"未知語:その他 品詞推定:特殊 疑似代表表記 代表表記:;/;"><品曖-その他><記英数カ><英記号><記号><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
EOS
"""
        # <格解析結果:表示/ひょうじ:動2:ガ/N/;/1/0/1;ヲ/U/-/-/-/-;ニ/U/-/-/-/-;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;修飾/U/-/-/-/-;ニヨル/U/-/-/-/-;トスル/U/-/-/-/-;ニツク/U/-/-/-/-;ニモトヅク/U/-/-/-/-;ニアワセル/U/-/-/-/-;ニタイスル/U/-/-/-/-;ニオク/U/-/-/-/->
        pas = Pas(tid=0, result=BList(spec))

        self.assertEqual(pas.cfid, "表示/ひょうじ:動2")

        self.assertEqual(pas.arguments["ガ"][0].sid, "1")
        self.assertEqual(pas.arguments["ガ"][0].tid, 1)
        self.assertEqual(pas.arguments["ガ"][0].midasi, ";")
        self.assertEqual(pas.arguments["ガ"][0].flag, "N")
        self.assertEqual(pas.arguments["ガ"][0].sdist, 0)


if __name__ == '__main__':
    unittest.main()
