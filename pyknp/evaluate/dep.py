#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyknp.knp.blist import BList
from pyknp.evaluate.scorer import Scorer


def dependency(g, s, level=2, checkType=False, ignoreStart=True):
    assert isinstance(g, BList)
    assert isinstance(s, BList)
    assert isinstance(level, int)
    assert isinstance(checkType, bool)
    assert isinstance(ignoreStart, bool)
    if level != 1 and level != 2:
        raise KeyError

    spans = set([])
    g_spans = [g.get_tag_span(t.tag_id) for t in g.tag_list()]
    s_spans = [s.get_tag_span(t.tag_id) for t in s.tag_list()]
    if ignoreStart:
        for i, g_span in enumerate(g_spans):
            g_spans[i] = g_span[1]
        for i, s_span in enumerate(s_spans):
            s_spans[i] = s_span[1]
    spans = spans.union(set(g_spans))
    spans = spans.union(set(s_spans))

    scorer = Scorer()
    for span in spans:
        g_to_span = None
        s_to_span = None
        g_dpndtype = None
        s_dpndtype = None
        try:
            gold_pid = g_spans.index(span)
            if (level == 2) and (gold_pid == len(g_spans) - 2):
                continue
            g_to = g.tag_list()[gold_pid].parent_id
            if g_to == -1:
                continue
            g_dpndtype = g.tag_list()[gold_pid].dpndtype
            g_to_span = g_spans[g_to]
        except ValueError:
            pass
        try:
            sys_pid = s_spans.index(span)
            s_to = s.tag_list()[sys_pid].parent_id
            if s_to == -1:
                continue
            s_dpndtype = s.tag_list()[sys_pid].dpndtype
            s_to_span = s_spans[s_to]
        except ValueError:
            pass

        if g_to_span is None:
            if s_to_span is None:
                scorer.tn += 1  # Never reach
            else:
                scorer.fp += 1
        else:
            if s_to_span is None:
                scorer.fn += 1
            else:
                if g_to_span == s_to_span:
                    if checkType:
                        if g_dpndtype == s_dpndtype:
                            scorer.tp += 1
                        else:
                            scorer.fp += 1
                            scorer.fn += 1
                    else:
                        scorer.tp += 1
                else:
                    scorer.fp += 1
                    scorer.fn += 1

    return scorer
