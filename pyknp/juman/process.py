import sys
import os
import six
import re
import signal
import socket
import subprocess

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

    def __init__(self, command, timeout=180):
        self.subproc_args = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT }
        self.command=command

    def query(self, sentence, pattern):
        assert(isinstance(sentence, six.text_type))
        proc = subprocess.run(self.command, input=sentence.encode(), check=True, **self.subproc_args)
        result = ""
        for line in proc.stdout.decode().split("\n"):
            if re.search(pattern, line):
                break
            result = "%s%s\n" % (result, line)
        return result
