#-*- encoding: utf-8 -*-

import re
import shlex
import unittest

class Morpheme(object):
    """
    形態素の各種情報を保持するオブジェクト．
    """
    def __init__(self, spec, mrph_id=""):
        self.mrph_id = mrph_id
        self.doukei = []
        # shlex doesn't support unicode
        parts = map(lambda s: s.decode('utf-8'), shlex.split(spec.encode('utf-8')))
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
            self.imis = parts[11]
            self.fstring = parts[12]
        except IndexError:
            pass
        # Extract 代表表記
        self.repname = ''
        match = re.search(ur"代表表記:([^\"\s]+)", self.imis)
        if match:
            self.repname = match.group(1)
    def push_imis(self, imis):
        if self.imis == 'NIL':
            self.imis = '"%s"' % ' '.join(imis)
        else:
            self.imis = '%s%s"' % (self.imis[:-1], ' '.join(' ', imis))
    def push_doukei(self, mrph):
        self.doukei.append(mrph)
    def spec(self):
        imis = self.imis
        if ' ' in imis:
            imis = '"%s"' % imis
        spec = "%s %s %s %s %s %s %s %s %s %s %s %s %s" % \
                (self.midasi, self.yomi, self.genkei, self.hinsi, self.hinsi_id,
                 self.bunrui, self.bunrui_id, self.katuyou1, self.katuyou1_id,
                 self.katuyou2, self.katuyou2_id, imis, self.fstring)
        return "%s\n" % spec.strip()

class MorphemeTest(unittest.TestCase):
    def test_simple(self):
        spec = u"であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18\n"
        mrph = Morpheme(spec)
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
        self.assertEqual(mrph.spec(), spec)
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

if __name__ == '__main__':
    unittest.main()
