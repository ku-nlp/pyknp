#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import Juman, Jumanpp
from pyknp import Socket, Subprocess  # TODO(john): move to separate file
from pyknp import BList
import os
import sys
import unittest
import six


class KNP(object):
    """
    KNP を用いて構文解析を行うモジュールである．
    """

    def __init__(self, command='knp', server=None, port=31000, timeout=60,
                 option='-tab', rcfile='', pattern=r'EOS',
                 jumancommand='juman', jumanrcfile='', jumanpp=False):
        self.command = command
        self.server = server
        self.port = port
        self.timeout = timeout
        self.option = option
        self.rcfile = rcfile
        self.pattern = pattern
        self.socket = None
        self.subprocess = None
        self.jumanpp = (jumancommand == "jumanpp") or jumanpp

        if self.rcfile and not os.path.isfile(os.path.expanduser(self.rcfile)):
            sys.stderr.write("Can't read rcfile (%s)!\n" % self.rcfile)
            quit(1)

        if(self.jumanpp):
            self.juman = Jumanpp()
        else:
            self.juman = Juman(command=jumancommand, rcfile=jumanrcfile)

    def knp(self, sentence):
        self.parse(sentence)

    def parse(self, sentence):
        """
        文字列 sentence を対象として構文解析を行い，構文解析結果オブジェクトを返す．
        """
        assert(isinstance(sentence, six.text_type))
        juman_lines = self.juman.juman_lines(sentence)
        juman_str = "%s%s" % (juman_lines, self.pattern)
        if not self.socket and not self.subprocess:
            if self.server is not None:
                self.socket = Socket(
                    self.server, self.port, "RUN -tab -normal\n")
            else:
                command = "%s %s" % (self.command, self.option)
                if self.rcfile:
                    command += " -r %s" % self.rcfile
                self.subprocess = Subprocess(command)

        if self.socket:
            knp_lines = self.socket.query(juman_str, pattern=self.pattern)
        else:
            knp_lines = self.subprocess.query(juman_str, pattern=self.pattern)
        return BList(knp_lines, self.pattern)

    def result(self, input_str):
        return BList(input_str, self.pattern)


class KNPTest(unittest.TestCase):

    def setUp(self):
        self.knp = KNP()

    def test_dpnd(self):
        result = self.knp.parse(u"赤い花が咲いた。")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].parent.bnst_id, 1)
        self.assertEqual(len(result[1].children), 1)
        self.assertEqual(result[1].children[0].bnst_id, 0)
        self.assertEqual(result[1].parent.bnst_id, 2)
        self.assertEqual(result[2].parent, None)

    def test_mrph(self):
        result = self.knp.parse(u"赤い花が咲いた。")
        self.assertEqual(
            ''.join([mrph.midasi for mrph in result[0].mrph_list()]), u'赤い')
        self.assertEqual(
            ''.join([mrph.midasi for mrph in result[1].mrph_list()]), u'花が')
        self.assertEqual(
            ''.join([mrph.midasi for mrph in result[2].mrph_list()]), u'咲いた。')

if __name__ == '__main__':
    unittest.main()
