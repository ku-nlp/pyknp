#-*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import re
import unittest
import six
from six import u


class Morpheme(object):
    """
    形態素の各種情報を保持するオブジェクト．
    """

    def __init__(self, spec, mrph_id=None, newstyle=False):
        assert isinstance(spec, six.text_type)
        assert mrph_id is None or isinstance(mrph_id, int)
        if newstyle and mrph_id is None:
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
        if newstyle:
            self._parse_new_spec(spec.strip("\n"))
        else:
            self._parse_spec(spec.strip("\n"))
    
    def _parse_new_spec(self, spec):
        parts = spec.split(u"\t")
        assert parts[0] == u"-"
        self.mrph_id = int(parts[1])
        self.prev_mrph_id = [int(mid) for mid in parts[2].split(u";")]
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
        self.feature = self.parse_fstring(self.fstring)
        self.repname = parts[6]

    def _parse_spec(self, spec):
        parts = []
        part = ''
        inside_quotes = False
        if(spec.startswith(u'\  \  \  特殊 1 空白 6 * 0 * 0')):
            parts = [u'\ ',u'\ ',u'\ ',u'特殊',u'1',u'空白','6',u'*',u'0',u'*',u'0',u'NIL']
        else:
            for char in spec:
                if char == u'"':
                    if not inside_quotes:
                        inside_quotes = True
                    else:
                        inside_quotes = False
                if char == u' ' and not inside_quotes:
                    if part.startswith(u'"') and part.endswith(u'"'):
                        parts.append(part[1:-1])
                    else:
                        parts.append(part)
                    part = ''
                else:
                    part += char
            parts.append(part)

        try:
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
        """
        形態素の代表表記（曖昧性がある場合は「?」で連結）を返す．
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
        assert isinstance(prev_mrph_id, int) or isinstance(prev_mrph_id, six.text_type) or isinstance(prev_mrph_id, list) or prev_mrph_id is None
        if(prev_mrph_id is None):
            prev_mrph_id = self.prev_mrph_id
        
        # This method accepts character position instead of morpheme span for backward comatibility.
        assert isinstance(span, tuple) or isinstance(span, list) or isinstance(span, int) or isinstance(span, six.text_type) or span is None
        if(span is None):
            span = self.span
        elif(isinstance(span, tuple) or isinstance(span, list)):
            span = (span[0], span[1])
        elif(span is six.text_type):
            span = (int(span), int(span) + len(self.midasi) -1)
        elif(isinstance(span, int)):
            span = (span, span + len(self.midasi) -1)
        
        if self.mrph_id is None:
            raise NotImplementedError
        
        out = []
        out.append(u"-\t%s" % self.mrph_id)
        if isinstance(prev_mrph_id, list):
            out.append(u"\t%s" % u";".join([u"%s" % pm for pm in prev_mrph_id]))
        else:
            out.append(u"\t%s" % prev_mrph_id)
        out.append(u"\t%d\t%d" % span)
        out.append(u"\t%s" % self.midasi)
        if len(self.repname) == 0:
            #             out.append(u"\t%s/%s" % (self.midasi, self.yomi))
            out.append(u"\t%s/%s" % (self.genkei, self.genkei))
        else:
            out.append(u"\t%s" % self.repname)
        out.append(u"\t%s\t%s\t%s\t%s" % (self.yomi, self.genkei, self.hinsi, self.hinsi_id))
        out.append(u"\t%s\t%s\t%s\t%s\t%s\t%s" % (self.bunrui, self.bunrui_id, self.katuyou1, self.katuyou1_id, self.katuyou2, self.katuyou2_id))
        out.append(u"\t")
        if len(self.fstring) == 0:
            fs = []
            for im in self.imis.split(u" "):
                if im.startswith(u"代表表記:"):
                    continue
                elif im == u"NIL":
                    continue
                fs.append(im)
            out.append(u"|".join(fs))
        else:
            out.append(self.fstring)
        out.append(u"\n")
        return u"".join(out)
    
    def parse_fstring(self, fstring):
        rvalue = {}
        for feature in fstring.split(u"|"):
            fs = feature.rstrip().lstrip().split(u":")
            key = ":".join(fs[:-1])
            val = fs[-1]
            rvalue[key]=val.split(u";")
        return rvalue

class MorphemeTest(unittest.TestCase):

    def test_simple(self):
        spec = u"であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18\n"
        mrph = Morpheme(spec, 123)
        self.assertEqual(mrph.midasi, u'であり')
        self.assertEqual(mrph.yomi, u'であり')
        self.assertEqual(mrph.genkei, u'だ')
        self.assertEqual(mrph.hinsi, u'判定詞')
        self.assertEqual(mrph.hinsi_id, 4)
        self.assertEqual(mrph.bunrui, u'*')
        self.assertEqual(mrph.bunrui_id, 0)
        self.assertEqual(mrph.katuyou1, u'判定詞')
        self.assertEqual(mrph.katuyou1_id, 25)
        self.assertEqual(mrph.katuyou2, u'デアル列基本連用形')
        self.assertEqual(mrph.katuyou2_id, 18)
        self.assertEqual(mrph.fstring, "")
        self.assertEqual(mrph.spec(), spec)
        self.assertEqual(mrph.new_spec(8, 9), u"-\t123\t8\t9\t11\tであり\tだ/だ\tであり\tだ\t判定詞\t4\t*\t0\t判定詞\t25\tデアル列基本連用形\t18\t\n")

    def test_imis(self):
        spec = u"""解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0 "代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術"\n"""
        mrph = Morpheme(spec)
        self.assertEqual(mrph.spec(), spec)
        self.assertEqual(mrph.imis, u"代表表記:解析/かいせき カテゴリ:抽象物 ドメイン:教育・学習;科学・技術")

    def test_nil(self):
        spec = u"であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18 NIL\n"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.imis, "NIL")
        self.assertEqual(mrph.spec(), spec)

    def test_at(self):
        spec = u"@ @ @ 未定義語 15 その他 1 * 0 * 0"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.midasi, u'@')

    def test_knp(self):
        spec = u"構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0 NIL <漢字><かな漢字><自立><←複合><名詞相当語>\n"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.midasi, u'構文')
        self.assertEqual(mrph.yomi, u'こうぶん')
        self.assertEqual(mrph.genkei, u'構文')
        self.assertEqual(mrph.hinsi, u'名詞')
        self.assertEqual(mrph.hinsi_id, 6)
        self.assertEqual(mrph.bunrui, u'普通名詞')
        self.assertEqual(mrph.bunrui_id, 1)
        self.assertEqual(mrph.katuyou1, u'*')
        self.assertEqual(mrph.katuyou1_id, 0)
        self.assertEqual(mrph.katuyou2, u'*')
        self.assertEqual(mrph.katuyou2_id, 0)
        self.assertEqual(mrph.imis, u'NIL')
        self.assertEqual(mrph.fstring, u'<漢字><かな漢字><自立><←複合><名詞相当語>')
        self.assertEqual(mrph.spec(), spec)


class MorphemeTest2(unittest.TestCase):

    def test_simple(self):
        spec = u"""-	36	2	2	4	貰った	貰う/もらう	もらった	もらう	動詞	2	*	0	子音動詞ワ行	12	タ形	10	付属動詞候補（タ系）\n"""

        mrph = Morpheme(spec, 36, newstyle=True)
        self.assertEqual(mrph.midasi, u'貰った')
        self.assertEqual(mrph.yomi, u'もらった')
        self.assertEqual(mrph.genkei, u'もらう')
        self.assertEqual(mrph.hinsi, u'動詞')
        self.assertEqual(mrph.hinsi_id, 2)
        self.assertEqual(mrph.bunrui, u'*')
        self.assertEqual(mrph.bunrui_id, 0)
        self.assertEqual(mrph.katuyou1, u'子音動詞ワ行')
        self.assertEqual(mrph.katuyou1_id, 12)
        self.assertEqual(mrph.katuyou2, u'タ形')
        self.assertEqual(mrph.katuyou2_id, 10)
        self.assertEqual(mrph.imis, '')
        self.assertEqual(mrph.fstring, u"付属動詞候補（タ系）")
        self.assertEqual(mrph.spec(), u"貰った もらった もらう 動詞 2 * 0 子音動詞ワ行 12 タ形 10  付属動詞候補（タ系）\n")
        self.assertEqual(mrph.new_spec(2, 2), spec)

    def test_doukei(self):
        spec1 = u"""-	1	0	0	0	母	母/ぼ	ぼ	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:音|漢字\n"""
        spec2 = u"""-	2	0	0	0	母	母/はは	はは	母	名詞	6	普通名詞	1	*	0	*	0	漢字読み:訓|カテゴリ:人|漢字\n"""
        m1 = Morpheme(spec1, 1, newstyle=True)
        m2 = Morpheme(spec2, 1, newstyle=True)
        m1.push_doukei(m2)
        self.assertEqual(m1.repnames(), u"母/ぼ?母/はは")


if __name__ == '__main__':
    unittest.main()
