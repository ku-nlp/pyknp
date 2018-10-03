import sys
import os
import six
import re
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

    def __init__(self, command):
        subproc_args = {'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE,
                'stderr': subprocess.STDOUT, 'cwd': '.',
                'close_fds': sys.platform != "win32"}
        try:
            env = os.environ.copy()
            self.process = subprocess.Popen(command, env=env, **subproc_args)
        except OSError:
            raise
        (self.stdouterr, self.stdin) = (self.process.stdout, self.process.stdin)

    def __del__(self):
        self.process.stdin.close()
        self.process.stdout.close()
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
            line = self.stdouterr.readline().rstrip().decode('utf-8')
            if re.search(pattern, line):
                break
            result = "%s%s\n" % (result, line)
        return result
        
