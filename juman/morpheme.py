#-*- encoding: utf-8 -*-

import sys
import unittest

class Morpheme:
    def __init__(self, spec, id=""):
        self.spec = spec
        self.id = id
        self.doukei = []
        parts = self.spec.split()
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
        except:
            pass
    def push_imis(self, imis):
        if self.imis == 'NIL':
            self.imis = '"%s"' % ' '.join(imis)
        else:
            self.imis = '%s%s"' % (self.imis[:-1], ' '.join(' ', imis))
    def repname(self):
        groups = re.match(r"代表表記:([^\"\s]+)", self.imis)
        if groups:
            return groups.group(1)
        return ""
    def repnames(self, flag):
        ret = []
        rep = self.repname
        if not rep:
            rep = this.make_repname()
        if rep:
            ret.append(rep)
        if self.repname and not (flag and self.spec == "<音訓解消>"):
            ret.append(self.get_doukei_reps())
        # TODO(john): remove duplicates
        return '?'.join(ret);
    def get_doukei_reps(self):
        reps = []
        for doukei in self.doukei():
            rep = doukei.repname()
            if not rep:
                rep = doukei.make_repname()
            if rep:
                reps.append(rep)
        return reps
    def make_repname(self):
        new_m = self.change_katuyou2('基本形');
        if new_m:
            return "%s/%s" % (new_m.genkei, new_m.yomi)
        return "%s/%s" % (self.genkei, self.yomi)
    def kanou_dousi(self):
        groups = re.match(r"可能動詞:([^\"\s]+)/)", self.imis)
        if groups:
            return groups[1]
        return ""
    def push_doukei(self, doukei):
        self.doukei.append(doukei)
    def spec(self):
        spec = ""
        if self.midasi: spec = "%s%s " % self.midasi
        if self.yomi: spec = "%s%s " % self.yomi
        if self.genkei: spec = "%s%s " % self.genkei
        if self.hinsi: spec = "%s%s " % self.hinsi
        if self.hinsi_id: spec = "%s%d " % self.hinsi_id
        if self.bunrui: spec = "%s%s " % self.bunrui
        if self.bunrui_id: spec = "%s%d " % self.bunrui_id
        if self.katuyou1: spec = "%s%s " % self.katuyou1
        if self.katuyou1_id: spec = "%s%d " % self.katuyou1_id
        if self.katuyou2: spec = "%s%s " % self.katuyou2
        if self.katuyou2_id: spec = "%s%d " % self.katuyou2_id
        if self.imis: spec = "%s%s " % self.imis
        return spec.strip()

class MorphemeTest(unittest.TestCase):
    def test_simple(self):
        spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18\n"
        mrph = Morpheme(spec)
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
        self.assertEqual(mrph.spec, spec)
    def test_nil(self):
        spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18 NIL\n"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.imis, "NIL")
        self.assertEqual(mrph.spec, spec)
    def test_at(self):
        spec = "@ @ @ 未定義語 15 その他 1 * 0 * 0"
        mrph = Morpheme(spec)
        self.assertEqual(mrph.midasi, '@')

if __name__ == '__main__':
    unittest.main()
