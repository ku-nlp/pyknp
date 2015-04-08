#-*- encoding: utf-8 -*-

from morpheme import Morpheme
from mlist import MList

mlist = MList()
mlist.push_mrph(Morpheme("構文 こうぶん 構文 名詞 6 普通名詞 1 * 0 * 0\n"))
mlist.push_mrph(Morpheme("解析 かいせき 解析 名詞 6 サ変名詞 2 * 0 * 0\n"))

assert(len(mlist.mrph) == 2)
assert(mlist.mrph[0].midasi == '構文')
assert(mlist.mrph[-1].midasi == '解析')
assert(''.join([x.midasi for x in mlist.mrph_list()]) == '構文解析')
