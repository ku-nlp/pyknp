import os
import re
import socket
import subprocess
import sys

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
        assert (isinstance(sentence, six.text_type))
        sentence = sentence.strip() + '\n'  # ensure sentence ends with '\n'
        self.sock.sendall(sentence.encode('utf-8'))
        data = self.sock.recv(1024)
        recv = data
        while not re.search(pattern, recv):
            data = self.sock.recv(1024)
            recv = "%s%s" % (recv, data)
        return recv.strip().decode('utf-8')


class Subprocess(object):

    def __init__(self, command, timeout=180):
        self.subproc_args = {'stdout': subprocess.PIPE, 'stdout': subprocess.STDOUT, 'timeout': timeout, 'cwd': '.',
                             'close_fds': sys.platform != "win32"}
        self.command = command

    def query(self, sentence, pattern):
        assert (isinstance(sentence, six.text_type))
        env = os.environ.copy()
        proc = subprocess.run(self.command, input=(sentence + '\n').encode(), env=env, check=True, **self.subproc_args)
        result = ''
        for line in proc.stdout.decode().split("\n"):
            if re.search(pattern, line):
                break
            result += line + '\n'
        return result
