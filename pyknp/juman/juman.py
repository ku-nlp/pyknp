#-*- encoding: utf-8 -*-

from pyknp import MList
from pyknp import Morpheme
import os
import re
import socket
import subprocess
import unittest

VERSION = '0.5.7'

class Socket(object):
    def __init__(self, hostname, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((hostname, port))
        except:
            raise
        self.sock.send("RUN -e2\n")
        data = ""
        while "OK" not in data:
            data = self.sock.recv(1024)
    def __del__(self):
        if self.sock:
            self.sock.close()
    def query(self, sentence, pattern):
        assert(isinstance(sentence, unicode))
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
                        'stderr': subprocess.STDOUT, 'cwd': '.', 'close_fds' : True}
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
    def query(self, sentence, pattern):
        assert(isinstance(sentence, unicode))
        self.process.stdin.write("%s\n" % sentence.encode('utf-8'))
        result = ""
        while True:
            line = self.stdouterr.readline()[:-1]
            if re.search(pattern, line):
                break
            result = "%s%s\n" % (result, line.decode('utf-8'))
        return result

class Juman(object):
    def __init__(self, command='juman', server='', port=32000, timeout=30,
                 option='-e2 -B', rcfile='~/.jumanrc', ignorepattern='',
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
        if self.server != '':
            self.socket = Socket(self.server, self.port)
        else:
            self.subprocess = Subprocess(self.command)
        #if self.rcfile != '' and self.server != '':
        #    sys.stderr.write("Warning: rcfile option may not work with Juman server.\n")
    def juman_lines(self, input_str):
        if self.socket:
            return self.socket.query(input_str, pattern=self.pattern)
        return self.subprocess.query(input_str, pattern=self.pattern)
    def juman(self, input_str):
        assert(isinstance(input_str, unicode))
        result = MList(self.juman_lines(input_str))
        return result
    def analysis(self, input_str):
        return self.juman(input_str)

class JumanTest(unittest.TestCase):
    def setUp(self):
        #self.juman = Juman(server='localhost')
        self.juman = Juman()
    def test_normal(self):
        test_str = u"この文を解析してください。"
        result = self.juman.analysis(test_str)
        self.assertEqual(len(result), 7)
        self.assertEqual(''.join(mrph.midasi for mrph in result), test_str)
        self.assertGreaterEqual(len(result.spec().split("\n")), 7)
    #def test_space(self):
        #result = self.juman.analysis("「 」を含む文")
        #self.assertEqual(result.mrph[1].midasi, ' ')
    #def test_backslash(self):
        #result = self.juman.analysis("「\」を含む文")
        #self.assertEqual(result[1].midasi, '\\')
    #def test_at(self):
        #result = self.juman.analysis("「@」を含む文")
        #self.assertEqual(result[1].midasi, '@')

if __name__ == '__main__':
    unittest.main()
