#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyknp.knp.blist import BList
from pyknp.evaluate.scorer import Scorer


def dependency(g, s):
    assert isinstance(g, BList)
    assert isinstance(s, BList)

    spans = set([])
    g_spans = [g.get_tag_span(t.tag_id) for t in g.tag_list()]
    s_spans = [s.get_tag_span(t.tag_id) for t in s.tag_list()]
    spans = spans.union(set(g_spans))
    spans = spans.union(set(s_spans))

    scorer = Scorer()
    for span in spans:
        g_to_span = None
        s_to_span = None
        try:
            gold_pid = g_spans.index(span)
            g_to = g.tag_list()[gold_pid].parent_id
            if g_to == -1:
                continue
            g_to_span = g_spans[g_to]
        except ValueError:
            pass
        try:
            sys_pid = s_spans.index(span)
            s_to = s.tag_list()[sys_pid].parent_id
            if s_to == -1:
                continue
            s_to_span = s_spans[s_to]
        except ValueError:
            pass

        if g_to_span is None:
            if s_to_span is None:
                scorer.tn += 1
            else:
                scorer.fp += 1
        else:
            if g_to_span == s_to_span:
                scorer.tp += 1
            else:
                scorer.fn += 1

    return scorer
