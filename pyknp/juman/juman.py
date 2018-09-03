#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from pyknp import MList
from pyknp import Morpheme
import os
import sys
import re
import socket
import subprocess
import unittest
import six


class Socket(object):

    def __init__(self, hostname, port, option=None):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((hostname, port))
        except:
            raise
        if option is not None:
            self.sock.send(option)
        data = ""
        while "OK" not in data:
            data = self.sock.recv(1024)

    def __del__(self):
        if self.sock:
            self.sock.close()

    def query(self, sentence, pattern):
        assert(isinstance(sentence, six.text_type))
        self.sock.sendall("%s\n" % sentence.encode('utf-8').strip())
        data = self.sock.recv(1024)
        recv = data
        while not re.search(pattern, recv):
            data = self.sock.recv(1024)
            recv = "%s%s" % (recv, data)
        return recv.strip().decode('utf-8')


class Subprocess(object):

    def __init__(self, command):
        subproc_args = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT, 'cwd': '.',
                'close_fds': sys.platform != "win32"}
        try:
            env = os.environ.copy()
            self.process = subprocess.Popen('bash -c "%s"' % command, env=env,
                                            shell=True, **subproc_args)
        except OSError:
            raise
        (self.stdouterr, self.stdin) = (self.process.stdout, self.process.stdin)

    def __del__(self):
        self.process.stdin.close()
        try:
            self.process.kill()
            self.process.wait()
        except OSError:
            pass
        except TypeError:
            pass
        except AttributeError:
            pass


    def query(self, sentence, pattern):
        assert(isinstance(sentence, six.text_type))
        self.process.stdin.write(sentence.encode('utf-8')+six.b('\n'))
        self.process.stdin.flush()
        result = ""
        while True:
            line = self.stdouterr.readline()[:-1].decode('utf-8')
            if re.search(pattern, line):
                break
            result = "%s%s\n" % (result, line)
        return result
        

class Juman(object):
    """
    形態素解析器 JUMAN を Python から利用するためのモジュール
    """

    def __init__(self, command='jumanpp', server=None, port=32000, timeout=30,
                 option='', rcfile='', ignorepattern='',
                 pattern=r'^EOS$', jumanpp=True):
        """
        Args:
            command (str): Jumanコマンド
            option (str): Jumanオプション (-e2, -B など)
        """
        if jumanpp or command != 'jumanpp':
            self.command = command
            self.option = option
        else:
            self.command = 'juman'
            self.option = option+' -e2 -B' 
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

    def juman_lines(self, input_str):
        """ 入力文字列に対して形態素解析を行い、そのJuman出力結果を返す

        Args:
            input_str (str): 文を表す文字列

        Returns:
            str: Juman出力結果
        """
        if '\n' in input_str:
            input_str = input_str.replace('\n','')
            print('Analysis is done ignoring "\\n".', file=sys.stderr)
        if not self.socket and not self.subprocess:
            if self.server is not None:
                self.socket = Socket(self.server, self.port, "RUN -e2\n")
            else:
                command = "%s %s" % (self.command, self.option)
                if 'jumanpp' not in self.command and self.rcfile:
                    command += " -r %s" % self.rcfile
                self.subprocess = Subprocess(command)
        if self.socket:
            return self.socket.query(input_str, pattern=self.pattern)
        return self.subprocess.query(input_str, pattern=self.pattern)

    def juman(self, input_str):
        """ analysis関数と同じ """
        assert(isinstance(input_str, six.text_type))
        result = MList(self.juman_lines(input_str))
        return result

    def analysis(self, input_str):
        """ 入力文字列に対して形態素解析し、その結果を MList オブジェクトとして返す
        
        Args:
            input_str (str): 文を表す文字列

        Returns:
            MList: 形態素列オブジェクト
        """
        return self.juman(input_str)

    def result(self, input_str):
        """ Juman出力結果に対して、その結果を MList オブジェクトとして返す
        
        Args:
            input_str (str): Juman出力結果

        Returns:
            MList: 形態素列オブジェクト
        """
        return MList(input_str)


class JumanTest(unittest.TestCase):

    def setUp(self):
        self.jumanpp = Juman()
        self.juman = Juman(jumanpp=False)

    
    # JUMANPP
    def test_normal_jumanpp(self):
        test_str = u"この文を解析してください。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

    def test_nominalization_jumanpp(self):
        test_str = u"音の響きを感じる。"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 6)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 6)
        self.assertEqual(result[2].midasi, u"響き")
        self.assertEqual(result[2].hinsi, u"名詞")
    
    def test_whitespace_jumanpp(self):
        test_str = u"半角 スペース"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(len(result), 3)
        self.assertEqual((result[1].bunrui == u'空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(u" ", u"\ "))
        self.assertGreaterEqual(len(result.spec().split("\n")), 3)

    def test_eos(self):
        test_str = u"エネルギーを素敵にENEOS"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_eos2(self):
        test_str = u"Canon EOS 80D買った"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(u" ", u"\ "))

    def test_dquo(self):
        test_str = u"\"最高\"の気分"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_escape(self):
        test_str = u"&lt;tag&gt;\\エス\'ケープ"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    def test_cr(self):
        test_str = u"これは\rどう"
        result = self.jumanpp.analysis(test_str)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)

    # JUMAN 
    def test_normal_juman(self):
        test_str = u"この文を解析してください。"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

    def test_whitespace_juman(self):
        test_str = u"半角 スペース"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 4) # 半|角|\ |スペース
        self.assertEqual((result[2].bunrui == u'空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str.replace(u" ", u"\ "))
        self.assertGreaterEqual(len(result.spec().split("\n")), 4)


if __name__ == '__main__':
    unittest.main()
