# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import re
import unittest
import six


class JUMAN_FORMAT(object):
    """ JUMANのラティスオプション

    Attributes:
        DEFAULT : 通常のJUMAN出力形式 (ラティスオプションなし)
        LATTICE_TOP_ONE: ラティス出力形式から、TOP1のビームだけを読む
        LATTICE_ALL: ラティス出力形式から、すべてのビームを読む 
    """

    DEFAULT = 0  # default
    LATTICE_TOP_ONE = 1
    LATTICE_ALL = 2


class Morpheme(object):
    """ 形態素の各種情報を保持するオブジェクト．

    Args:
        spec (str): JUMAN/KNP出力
        mrph_id (int): 形態素ID
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式
    
    Attributes:
        mrph_id (int): 形態素ID 
        mrph_index (int): mrph_idに同じ
        doukei (list): 
        midasi (str): 見出し
        yomi (str): 読み
        genkei (str): 原形
        hinsi (str): 品詞
        hinsi_id (int): 品詞ID
        bunrui (str): 品詞細分類
        bunrui_id (int): 品詞細分類ID
        katuyou1 (str): 活用型
        katuyou1_id (int): 活用型ID
        katuyou2 (str): 活用形
        katuyou2_id (int): 活用形ID
        imis (str): 意味情報
        fstring (str): 素性情報
        repname (str): 代表表記
        ranks (set[int]): ラティスでのランク
        span (tuple): 形態素の位置 (開始位置, 終了位置), JUMAN出力形式がラティス形式の場合のみ
    """

    def __init__(self, spec, mrph_id=None, juman_format=JUMAN_FORMAT.DEFAULT):
        assert isinstance(spec, six.text_type)
        assert mrph_id is None or isinstance(mrph_id, int)
        if juman_format != JUMAN_FORMAT.DEFAULT and mrph_id is None:
            raise KeyError
        self.mrph_index = mrph_id
        self.mrph_id = mrph_id
        self.prev_mrph_id = 0
        self.span = (0, 0)
        self.doukei = []
        self.midasi = ''
        self.yomi = ''
        self.genkei = ''
        self.hinsi = ''
        self.hinsi_id = 0
        self.bunrui = ''
        self.bunrui_id = 0
        self.katuyou1 = ''
        self.katuyou1_id = 0
        self.katuyou2 = ''
        self.katuyou2_id = 0
        self.imis = ''
        self.fstring = ''
        self.repname = ''
        self.ranks = {1}
        if juman_format == JUMAN_FORMAT.DEFAULT:
            self._parse_spec(spec.strip("\n"))
        else:
            self._parse_new_spec(spec.strip("\n"))
    
    def _parse_new_spec(self, spec):
        try:  # FIXME KNPの場合と同様、EOSをきちんと判定する
            parts = spec.split("\t")
            self.mrph_id = int(parts[1])
            self.prev_mrph_id = [int(mid) for mid in parts[2].split(";")]
            self.span = (int(parts[3]), int(parts[4]))
            self.midasi = parts[5]
            self.yomi = parts[7]
            self.genkei = parts[8]
            self.hinsi = parts[9]
            self.hinsi_id = int(parts[10])
            self.bunrui = parts[11]
            self.bunrui_id = int(parts[12])
            self.katuyou1 = parts[13]
            self.katuyou1_id = int(parts[14])
            self.katuyou2 = parts[15]
            self.katuyou2_id = int(parts[16])
            self.fstring = parts[17]
            self.feature = self._parse_fstring(self.fstring)
            self.repname = parts[6]
            ranks = self.feature.get('ランク', None)                 
            if ranks is not None:
                self.ranks = set(int(x) for x in ranks)
        except IndexError:
            pass

    def _parse_spec(self, spec):
        parts = []
        part = ''
        inside_quotes = False
        if spec.startswith(' '):
            spec = '\\%s' % spec
        if spec.startswith('\  \  \  特殊 1 空白 6 * 0 * 0'):
            parts = ['\ ', '\ ', '\ ', '特殊', '1', '空白', '6', '*', '0', '*', '0', 'NIL']
        else:
            for char in spec:
                if char == '"':
                    if not inside_quotes:
                        inside_quotes = True
                    else:
                        inside_quotes = False
                # If "\"" proceeds " ", it would be not inside_quotes, but "\"".
                if inside_quotes and char == ' ' and part == '"':
                    inside_quotes = False
                if part != "" and char == ' ' and not inside_quotes:
                    if part.startswith('"') and part.endswith('"') and len(part) > 1:
                        parts.append(part[1:-1])
                    else:
                        parts.append(part)
                    part = ''
                else:
                    part += char
            parts.append(part)

        try:  # FIXME KNPの場合と同様、EOSをきちんと判定する
            self.midasi = parts[0]
            self.yomi = parts[1]
            self.genkei = parts[2]
            self.hinsi = parts[3]
            self.hinsi_id = int(parts[4])
            self.bunrui = parts[5]
            self.bunrui_id = int(parts[6])
            self.katuyou1 = parts[7]
            self.katuyou1_id = int(parts[8])
            self.katuyou2 = parts[9]
            self.katuyou2_id = int(parts[10])
            self.imis = parts[11].lstrip("\"").rstrip("\"")
            self.fstring = parts[12]
        except IndexError:
            pass
        # Extract 代表表記
        match = re.search(r"代表表記:([^\"\s]+)", self.imis)
        if match:
            self.repname = match.group(1)

    def push_doukei(self, mrph):
        self.doukei.append(mrph)

    def repnames(self):
        """ 形態素の代表表記（曖昧性がある場合は「?」で連結）を返す．
        
        Returns:
            str: 形態素の代表表記文字列
        """
        repnames = []
        if self.repname:
            repnames.append(self.repname)
        for doukei in self.doukei:
            if doukei.repname:
                repnames.append(doukei.repname)
        # 重複を削除
        return "?".join(sorted(set(repnames), key=repnames.index))

    def spec(self):
        imis = self.imis
        if imis != "NIL" and len(imis) != 0:
            imis = '"%s"' % imis

        spec = "%s %s %s %s %s %s %s %s %s %s %s %s %s" % \
            (self.midasi, self.yomi, self.genkei, self.hinsi, self.hinsi_id,
             self.bunrui, self.bunrui_id, self.katuyou1, self.katuyou1_id,
             self.katuyou2, self.katuyou2_id, imis, self.fstring)
        return "%s\n" % spec.rstrip()

    def new_spec(self, prev_mrph_id=None, span=None):
        assert isinstance(prev_mrph_id, int) or \
               isinstance(prev_mrph_id, six.text_type) or \
               isinstance(prev_mrph_id, list) or \
               prev_mrph_id is None
        if prev_mrph_id is None:
            prev_mrph_id = self.prev_mrph_id
        
        # This method accepts character position instead of morpheme span for backward comatibility.
        assert isinstance(span, tuple) or \
               isinstance(span, list) or \
               isinstance(span, int) or \
               isinstance(span, six.text_type) or \
               span is None
        if span is None:
            span = self.span
        elif isinstance(span, tuple) or isinstance(span, list):
            span = (span[0], span[1])
        elif span is six.text_type:
            span = (int(span), int(span) + len(self.midasi) - 1)
        elif isinstance(span, int):
            span = (span, span + len(self.midasi) - 1)
        
        if self.mrph_id is None:
            raise NotImplementedError
        
        out = ["-\t%s" % self.mrph_id]
        if isinstance(prev_mrph_id, list):
            out.append("\t%s" % ";".join(["%s" % pm for pm in prev_mrph_id]))
        else:
            out.append("\t%s" % prev_mrph_id)
        out.append("\t%d\t%d" % span)
        out.append("\t%s" % self.midasi)
        if len(self.repname) == 0:
            #             out.append("\t%s/%s" % (self.midasi, self.yomi))
            out.append("\t%s/%s" % (self.genkei, self.genkei))
        else:
            out.append("\t%s" % self.repname)
        out.append("\t%s\t%s\t%s\t%s" % (self.yomi, self.genkei, self.hinsi, self.hinsi_id))
        out.append("\t%s\t%s\t%s\t%s\t%s\t%s" %
                   (self.bunrui, self.bunrui_id, self.katuyou1, self.katuyou1_id, self.katuyou2, self.katuyou2_id))
        out.append("\t")
        if len(self.fstring) == 0:
            fs = []
            for im in self.imis.split(" "):
                if im.startswith("代表表記:"):
                    continue
                elif im == "NIL":
                    continue
                fs.append(im)
            out.append("|".join(fs))
        else:
            out.append(self.fstring)
        out.append("\n")
        return "".join(out)

    def _parse_fstring(self, fstring):
        """ 素性情報をパースする """
        rvalue = {}
        for feature in fstring.split("|"):
            fs = feature.rstrip().lstrip().split(":")
            key = ":".join(fs[:-1])
            val = fs[-1]
            rvalue[key] = val.split(";")
        return rvalue


class MorphemeTest(unittest.TestCase):

    def test_simple(self):
        spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18\n"
        mrph = Morpheme(spec, 123)
        self.assertEqual(mrph.midasi, 'であり')
        self.assertEqual(mrph.yomi, 'であり')
        self.assertEqual(mrph.genkei, 'だ')
        self.assertEqual(mrph.hinsi, '判定詞')
        self.assertEqual(mrph.hinsi_id, 4)
        self.assertEqual(mrph.bunrui, '*')
        self.assertEqual(mrph.bunrui_id, 0)
        self.assertEqual(mrph.katuyou1, '判定詞')
        self.assertEqual(mrph.katuyou1_id, 25)
        self.assertEqual(mrph.katuyou2, 'デアル列基本連用形')
        self.assertEqual(mrph.katuyou2_id, 18)
        self.assertEqual(mrph.fstring, "")
        self.assertEqual(mrph.spec(), spec)
        self.assertEqual(mrph.new_spec(8, 9), "-\t123\t8\t9\t11\tであり\tだ/だ\tであり\tだ\t判定詞\t4\t*\t0\t判定詞\t25\tデアル列基本連用形\t18\t\n")

    def test_imis(self):
        spec = """解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術"\n"""
        mrph = Morpheme(spec)
        self.assertEqual(mrph.spec(), spec)
        self.assertEqual(mrph.imis, "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術")

    def test_nil(self):
        spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18 NIL\n"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.imis, "NIL")
        self.assertEqual(mrph.spec(), spec)

    def test_at(self):
        spec = "@ @ @ 未定義語 15 その他 1 * 0 * 0"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.midasi, '@')

    def test_knp(self):
        spec = "構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 NIL <漢字><かな漢字><自立><←複合><名詞相当語>\n"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.midasi, '構文')
        self.assertEqual(mrph.yomi, 'こうぶん')
        self.assertEqual(mrph.genkei, '構文')
        self.assertEqual(mrph.hinsi, '名詞')
        self.assertEqual(mrph.hinsi_id, 6)
        self.assertEqual(mrph.bunrui, '普通名詞')
        self.assertEqual(mrph.bunrui_id, 1)
        self.assertEqual(mrph.katuyou1, '*')
        self.assertEqual(mrph.katuyou1_id, 0)
        self.assertEqual(mrph.katuyou2, '*')
        self.assertEqual(mrph.katuyou2_id, 0)
        self.assertEqual(mrph.imis, 'NIL')
        self.assertEqual(mrph.fstring, '<漢字><かな漢字><自立><←複合><名詞相当語>')
        self.assertEqual(mrph.spec(), spec)


class MorphemeTest2(unittest.TestCase):

    def test_simple(self):
        spec = """-	36	2	2	4	貰った	貰う/もらう	もらった	もらう	動詞	2	*	0	子音動詞ワ行	12	タ形	10	付属動詞候補（タ系）\n"""

        mrph = Morpheme(spec, 36, juman_format=JUMAN_FORMAT.LATTICE_ALL)
        self.assertEqual(mrph.midasi, '貰った')
        self.assertEqual(mrph.yomi, 'もらった')
        self.assertEqual(mrph.genkei, 'もらう')
        self.assertEqual(mrph.hinsi, '動詞')
        self.assertEqual(mrph.hinsi_id, 2)
        self.assertEqual(mrph.bunrui, '*')
        self.assertEqual(mrph.bunrui_id, 0)
        self.assertEqual(mrph.katuyou1, '子音動詞ワ行')
        self.assertEqual(mrph.katuyou1_id, 12)
        self.assertEqual(mrph.katuyou2, 'タ形')
        self.assertEqual(mrph.katuyou2_id, 10)
        self.assertEqual(mrph.imis, '')
        self.assertEqual(mrph.fstring, "付属動詞候補（タ系）")
        self.assertEqual(mrph.spec(), "貰った もらった もらう 動詞 2 * 0 子音動詞ワ行 12 タ形 10  付属動詞候補（タ系）\n")
        self.assertEqual(mrph.new_spec(2, 2), spec)

    def test_doukei(self):
        spec1 = """-	1	0	0	0	母	母/ぼ	ぼ	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:音|漢字\n"""
        spec2 = """-	2	0	0	0	母	母/はは	はは	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:訓|カテゴリ:人|漢字\n"""
        m1 = Morpheme(spec1, 1, juman_format=JUMAN_FORMAT.LATTICE_ALL)
        m2 = Morpheme(spec2, 1, juman_format=JUMAN_FORMAT.LATTICE_ALL)
        m1.push_doukei(m2)
        self.assertEqual(m1.repnames(), "母/ぼ?母/はは")

    def test_ranks(self):
        spec1 = """-	1	0	0	0	母	母/ぼ	ぼ	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:音|漢字\n"""
        spec2 = """-	2	0	0	0	母	母/はは	はは	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:訓|カテゴリ:人|漢字|ランク:1;2;3\n"""
        m1 = Morpheme(spec1, 1, juman_format=JUMAN_FORMAT.LATTICE_ALL)
        m2 = Morpheme(spec2, 1, juman_format=JUMAN_FORMAT.LATTICE_ALL)
        self.assertEqual(1, len(m1.ranks))
        self.assertIn(1, m1.ranks)
        self.assertNotIn(2, m1.ranks)
        self.assertEqual(3, len(m2.ranks))
        self.assertIn(1, m2.ranks)
        self.assertIn(2, m2.ranks)
        self.assertIn(3, m2.ranks)
        self.assertNotIn(4, m2.ranks)        


if __name__ == '__main__':
    unittest.main()
