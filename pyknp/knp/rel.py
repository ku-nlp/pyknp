#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
import re

# language=RegExp
REL_PAT = r'rel type="(\S+?)"(?: mode="([^>]+?)")? target="(\S+?)"(?: sid="(.+?)" id="(.+?)")?/'
WRITER_READER_LIST = ["著者", "読者"]
WRITER_READER_CONV_LIST = {"一人称": "著者", "二人称": "読者"}


class Rel(object):

    def __init__(self, fstring):
        self.atype = None
        self.target = None
        self.sid = None
        self.tid = None
        self.mode = None
        self.ignore = False

        match = re.findall(REL_PAT, fstring)
        if len(match) == 0:
            self.ignore = True
            return
        atype, mode, target, sid, id_ = match[0]
        if mode == "？" and target == "なし":
            self.ignore = True

        if len(sid) == 0:
            sid = None  # dummy
            if target in WRITER_READER_CONV_LIST:
                target = WRITER_READER_CONV_LIST[target]
        if len(id_) == 0:
            id_ = None  # dummy
        if id_ is not None:
            id_ = int(id_)

        self.atype = atype
        self.target = target
        self.sid = sid
        self.tid = id_
        self.mode = mode

    def __repr__(self):
        if self.ignore:
            return 'Rel("")'
        specs = []
        specs.append('type="%s"' % self.atype)
        if self.mode:
            specs.append('mode="%s"' % self.mode)
        specs.append('target="%s"' % self.targtet)
        if self.sid:
            specs.append('sid="%s" id="%s"' % (self.sid, self.id))
        return 'Rel(%s)' % repr(' '.join(specs))
