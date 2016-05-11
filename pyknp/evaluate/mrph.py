#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyknp.knp.blist import BList
from pyknp.evaluate.scorer import Scorer


def morpheme(g, s, level):
    """
    level=0: segmentation のみ評価
    level=1: segmentation+POS の評価
    """
    assert isinstance(g, BList)
    assert isinstance(s, BList)
    assert isinstance(level, int)
    if level != 1 and level != 2:
        raise KeyError

    starts = set([])
    g_mrphs = g.mrph_list()
    s_mrphs = s.mrph_list()

    g_starts = [g.mrph_positions[t.mrph_id] for t in g_mrphs]
    s_starts = [s.mrph_positions[t.mrph_id] for t in s_mrphs]
    starts = starts.union(set(g_starts))
    starts = starts.union(set(s_starts))

    scorer = Scorer()
    for position in starts:
        g_id = None
        try:
            g_id = g_starts.index(position)
        except:
            scorer.fp += 1
            continue

        s_id = None
        try:
            s_id = s_starts.index(position)
        except:
            scorer.fn += 1
            continue

        g = g_mrphs[g_id]
        s = s_mrphs[s_id]
        if len(g.midasi) != len(s.midasi):
            scorer.fp += 1
            continue
        if level == 0:
            scorer.tp += 1
            continue

        # level=1
        if s.hinsi == u"未定義語":
            s.hinsi = u"名詞"
        if g.hinsi != s.hinsi:
            scorer.fp += 1
        else:
            scorer.tp += 1

    return scorer
