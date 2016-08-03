#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import collections
import six


class Argument(object):

    def __init__(self, sid, tid, rep, flag=None):
        assert isinstance(tid, int)
        assert isinstance(rep, six.text_type)
        self.sid = sid
        self.tid = tid
        self.rep = rep
        self.flag = flag


class Pas(object):

    def __init__(self, val=None, knpstyle=False):
        assert isinstance(knpstyle, bool)
        self.cfid = None
        self.arguments = collections.defaultdict(list)
        if val is None:
            return
        if knpstyle:
            self._parseKnpStyle(val)
            return
        raise ValueError

    def _parseKnpStyle(self, val):
        assert isinstance(val, six.text_type)
        c0 = val.find(u':')
        c1 = val.find(u':', c0 + 1)
        self.cfid = val[:c0] + u":" + val[c0 + 1:c1]

        if val.count(u":") < 2:  # For copula
            return

        for k in val[c1 + 1:].split(u';'):
            items = k.split(u"/")
            caseflag = items[1]
            if caseflag == u"U" or caseflag == u"-":
                continue

            mycase = items[0]
            rep = items[2]
            tid = int(items[3])
            sid = items[5]
            arg = Argument(sid, tid, rep, caseflag)

            self.arguments[mycase].append(arg)

if __name__ == '__main__':
    main()
