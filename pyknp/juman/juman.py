# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from pyknp import MList
from pyknp import JUMAN_FORMAT
from pyknp import Socket, Subprocess
import os
import sys
import unittest
import six
import distutils.spawn


class Juman(object):
    """形態素解析器 JUMAN を Python から利用するためのモジュール

    Args:
        command (str): JUMANの実行コマンド
        option (str): JUMAN解析オプション (ラティス形式 -s, ビーム幅 --beam <int>)
        rcfile (str): JUMAN設定ファイルへのパス
        pattern (str): JUMAN出力の終端記号
        jumanpp (bool): JUMAN++を用いるかJUMANを用いるか。commandを指定した場合は無視される。
    """

    def __init__(self, command='jumanpp', server=None, port=32000, timeout=30,
                 option='', rcfile='', ignorepattern='',
                 pattern=r'^EOS$', jumanpp=True):
        if jumanpp or command != 'jumanpp':
            self.command = command
            self.options = option.split()
        else:
            self.command = 'juman'
            self.options = option.split() + ['-e2', '-B']
        self.server = server
        self.port = port
        self.timeout = timeout
        self.rcfile = rcfile
        self.ignorepattern = ignorepattern
        self.pattern = pattern
        self.socket = None
        self.subprocess = None
        if self.rcfile and not os.path.isfile(os.path.expanduser(self.rcfile)):
            raise Exception("Can't read rcfile (%s)!" % self.rcfile)
        if distutils.spawn.find_executable(self.command) is None:
            raise Exception("Can't find JUMAN command: %s" % self.command)

    def juman_lines(self, input_str):
        """ 入力文字列に対して形態素解析を行い、そのJuman出力結果を返す

        Args:
            input_str (str): 文を表す文字列

        Returns:
            str: Juman出力結果
        """
        if '\n' in input_str:
            input_str = input_str.replace('\n', '')
            print('Analysis is done ignoring "\\n".', file=sys.stderr)
        if not self.socket and not self.subprocess:
            if self.server is not None:
                self.socket = Socket(self.server, self.port, "RUN -e2\n")
            else:
                command = [self.command] + self.options
                if 'jumanpp' not in self.command and self.rcfile:
                    command.extend(['-r', self.rcfile])
                self.subprocess = Subprocess(command)
        if self.socket:
            return self.socket.query(input_str, pattern=self.pattern)
        return self.subprocess.query(input_str, pattern=self.pattern)

    def juman(self, input_str, juman_format=JUMAN_FORMAT.DEFAULT):
        """ analysis関数と同じ """
        assert(isinstance(input_str, six.text_type))
        result = MList(self.juman_lines(input_str), juman_format)
        return result

    def analysis(self, input_str, juman_format=JUMAN_FORMAT.DEFAULT):
        """ 入力文字列に対して形態素解析し、その結果を MList オブジェクトとして返す
        
        Args:
            input_str (str): 文を表す文字列
            juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

        Returns:
            MList: 形態素列オブジェクト
        """
        return self.juman(input_str, juman_format)

    def result(self, input_str, juman_format=JUMAN_FORMAT.DEFAULT):
        """ Juman出力結果に対して、その結果を MList オブジェクトとして返す

        Args:
            input_str (str): Juman出力結果
            juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

        Returns:
            MList: 形態素列オブジェクト
        """
        return MList(input_str, juman_format)


class JumanTest(unittest.TestCase):

    def setUp(self):
        self.jumanpp = Juman()
        self.juman = Juman(jumanpp=False)

    # JUMANPP
    def test_normal_jumanpp(self):
        test_str = "この文を解析してください。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

    def test_nominalization_jumanpp(self):
        test_str = "音の響きを感じる。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 6)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 6)
        self.assertEqual(result[2].midasi, "響き")
        self.assertEqual(result[2].hinsi, "名詞")
    
    def test_whitespace_jumanpp(self):
        test_str = "半角 スペース"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 3)
        self.assertEqual((result[1].bunrui == '空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(" ", "\ "))
        self.assertGreaterEqual(len(result.spec().split("\n")), 3)

    def test_eos(self):
        test_str = "エネルギーを素敵にENEOS"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_eos2(self):
        test_str = "Canon EOS 80D買った"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(" ", "\ "))

    def test_dquo(self):
        test_str = "\"最高\"の気分"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_escape(self):
        test_str = "&lt;tag&gt;\\エス\'ケープ"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_cr(self):
        test_str = "これは\rどう"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    # JUMAN 
    def test_normal_juman(self):
        test_str = "この文を解析してください。"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

    def test_whitespace_juman(self):
        test_str = "半角 スペース"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 4)  # 半|角|\ |スペース
        self.assertEqual((result[2].bunrui == '空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(" ", "\ "))
        self.assertGreaterEqual(len(result.spec().split("\n")), 4)


if __name__ == '__main__':
    unittest.main()
