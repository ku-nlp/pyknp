#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import MList
from pyknp import Morpheme
from pyknp import Subprocess
import os
import sys
import re
import socket
import subprocess
import unittest
import six

class Jumanpp(object):
    """
    形態素解析器 JUMAN++ を Python から利用するためのモジュールである．
    """

    def __init__(self, command='jumanpp', timeout=30,
                 option='', pattern=r'EOS'):
        self.command = command
        self.timeout = timeout
        self.option = option
        self.rcfile = ''
        self.ignorepattern = ''
        self.pattern = pattern
        self.subprocess = None
        if self.rcfile and not os.path.isfile(os.path.expanduser(self.rcfile)):
            sys.stderr.write("Can't read rcfile (%s)!\n" % self.rcfile)
            quit(1)

    def jumanpp_lines(self, input_str):
        if not self.subprocess:
            command = "%s %s" % (self.command, self.option)
            self.subprocess = Subprocess(command)
        return self.subprocess.query(input_str, pattern=self.pattern)
    
    def juman_lines(self, input_str):
        return self.jumanpp_lines(input_str)

    def jumanpp(self, input_str):
        assert(isinstance(input_str, six.text_type))
        result = MList(self.jumanpp_lines(input_str))
        return result
    
    def juman(self, input_str):
        return self.jumanpp(input_str)

    def analysis(self, input_str):
        """
        指定された文字列 input_str を形態素解析し，その結果を MList オブジェクトとして返す．
        """
        return self.jumanpp(input_str)

    def result(self, input_str):
        return MList(input_str)

class JumanppTest(unittest.TestCase):

    def setUp(self):
        self.jumanpp = Jumanpp()

    def test_normal(self):
        test_str = u"この文を解析してください。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)
    
    def test_nominalization(self):
        test_str = u"音の響きを感じる。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 6)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 6)
        self.assertEqual(result[2].midasi, u"響き")
        self.assertEqual(result[2].hinsi, u"名詞")
    
    def test_whitespace(self):
        test_str = u"半角 スペース"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 3)
        self.assertEqual((result[1].bunrui == u'空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), u"半角\ スペース")
        self.assertGreaterEqual(len(result.spec().split("\n")), 3)

if __name__ == '__main__':
    unittest.main()
