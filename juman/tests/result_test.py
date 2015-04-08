#-*- encoding: utf-8 -*-

from result import Result

result = """形態素 けいたいそ 形態素 名詞 6 普通名詞 1 * 0 * 0
解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0
の の の 助詞 9 接続助詞 3 * 0 * 0
実行 じっこう 実行 名詞 6 サ変名詞 2 * 0 * 0
例 れい 例 名詞 6 普通名詞 1 * 0 * 0
@ 例 たとえ 例 名詞 6 普通名詞 1 * 0 * 0
@ 例 ためし 例 名詞 6 普通名詞 1 * 0 * 0
EOS"""

x = Result(result)
assert(len(x.mrph) == 5)
assert(''.join(y.midasi for y in x.mrph_list()) == "形態素解析の実行例")

x = Result(["%s\n" % x for x in result.split("\n")])
assert(len(x.mrph) == 5)

x = Result(result, pattern="^EOS$")
assert(len(x.mrph) == 5)
