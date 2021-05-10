#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyknp.knp.blist import BList
from pyknp.evaluate.scorer import Scorer


def phrase(g, s, level=0):
    assert isinstance(g, BList)
    assert isinstance(s, BList)
    assert isinstance(level, int)
    if level != 0:
        raise KeyError

    spans = set([])
    g_spans = [g.get_tag_span(t.tag_id) for t in g.tag_list()]
    s_spans = [s.get_tag_span(t.tag_id) for t in s.tag_list()]
    spans = spans.union(set(g_spans))
    spans = spans.union(set(s_spans))

    scorer = Scorer()
    for span in spans:
        try:
            _ = g_spans.index(span)
        except ValueError:
            scorer.fp += 1
            continue

        try:
            _ = s_spans.index(span)
        except ValueError:
            scorer.fn += 1
            continue

        scorer.tp += 1

    return scorer
