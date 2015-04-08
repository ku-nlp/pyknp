#-*- encoding: utf-8 -*-

from morpheme import Morpheme

spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18\n"
mrph = Morpheme(spec)

assert(mrph.midasi == 'であり')
assert(mrph.yomi == 'であり')
assert(mrph.genkei == 'だ')
assert(mrph.hinsi == '判定詞')
assert(mrph.hinsi_id == 4)
assert(mrph.bunrui == '*')
assert(mrph.bunrui_id == 0)
assert(mrph.katuyou1 == '判定詞')
assert(mrph.katuyou1_id == 25)
assert(mrph.katuyou2 == 'デアル列基本連用形')
assert(mrph.katuyou2_id == 18)
assert(mrph.spec == spec)

spec = "であり であり だ 判定詞 4 * 0 判定詞 25 デアル列基本連用形 18 NIL\n"
mrph = Morpheme(spec)
assert(mrph.imis == "NIL")
assert(mrph.spec == spec)

spec = "@ @ @ 未定義語 15 その他 1 * 0 * 0"
mrph = Morpheme(spec)
assert(mrph.midasi == '@')
