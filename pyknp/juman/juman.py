#-*- encoding: utf-8 -*-

from __future__ import absolute_import
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
    形態素解析器 JUMAN を Python から利用するためのモジュールである．
    """

    def __init__(self, command='juman', server=None, port=32000, timeout=30,
                 option='-e2 -B', rcfile='', ignorepattern='',
                 pattern=r'EOS'):
        self.command = command
        self.server = server
        self.port = port
        self.timeout = timeout
        self.option = option
        self.rcfile = rcfile
        self.ignorepattern = ignorepattern
        self.pattern = pattern
        self.socket = None
        self.subprocess = None
        if self.rcfile and not os.path.isfile(os.path.expanduser(self.rcfile)):
            sys.stderr.write("Can't read rcfile (%s)!\n" % self.rcfile)
            quit(1)

    def juman_lines(self, input_str):
        if not self.socket and not self.subprocess:
            if self.server is not None:
                self.socket = Socket(self.server, self.port, "RUN -e2\n")
            else:
                command = "%s %s" % (self.command, self.option)
                if self.rcfile:
                    command += " -r %s" % self.rcfile
                self.subprocess = Subprocess(command)
        if self.socket:
            return self.socket.query(input_str, pattern=self.pattern)
        return self.subprocess.query(input_str, pattern=self.pattern)

    def juman(self, input_str):
        assert(isinstance(input_str, six.text_type))
        result = MList(self.juman_lines(input_str))
        return result

    def analysis(self, input_str):
        """
        指定された文字列 input_str を形態素解析し，その結果を MList オブジェクトとして返す．
        """
        return self.juman(input_str)

    def result(self, input_str):
        return MList(input_str)


class JumanTest(unittest.TestCase):

    def setUp(self):
        self.juman = Juman()

    def test_normal(self):
        test_str = u"この文を解析してください。"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)

    def test_whitespace(self):
        test_str = u"半角 スペース"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 4) # 半|角|\ |スペース
        self.assertEqual((result[2].bunrui == u'空白'), True) 
        self.assertEqual(''.join(mrph.midasi for mrph in result), u"半角\ スペース")
        self.assertGreaterEqual(len(result.spec().split("\n")), 4)

if __name__ == '__main__':
    unittest.main()
