#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import re

REL_PAT = "rel type=\"([^\s]+?)\"(?: mode=\"([^>]+?)\")? target=\"([^\s]+?)\"(?: sid=\"(.+?)\" id=\"(.+?)\")?/"
WRITER_READER_LIST = [u"著者", u"読者"]
WRITER_READER_CONV_LIST = {u"一人称": u"著者", u"二人称": u"読者"}


class Rel(object):

    def __init__(self, fstring, consider_writer_reader=True):
        self.atype = None
        self.target = None
        self.sid = None
        self.tid = None
        self.mode = None
        self.ignore = False

        match = re.findall(r"%s" % REL_PAT, fstring)
        if len(match) == 0:
            self.ignore = True
            return
        atype, mode, target, sid, id = match[0]
        if mode == u"？":
            self.ignore = True
        if target == u"なし":
            self.ignore = True

        if len(sid) == 0:
            sid = None  # dummy
            if target in WRITER_READER_CONV_LIST:
                target = WRITER_READER_CONV_LIST[target]
        if len(id) == 0:
            id = None  # dummy
        if id is not None:
            id = int(id)

        self.atype = atype
        self.target = target
        self.sid = sid
        self.tid = id
        self.mode = mode
