#-*- encoding: utf-8 -*-

from juman import Juman
from juman import Socket, Subprocess  # TODO(john): move to separate file
from blist import BList
import unittest

VERSION = '0.4.9'

class KNP:
    def __init__(self, command='knp -tab', server='', port=31000, timeout=60,
            option='-tab', rcfile='~/.knprc', pattern=r'EOS'):
        self.command = command
        self.server = server
        self.port = port
        self.timeout = timeout
        self.option = option
        self.rcfile = rcfile 
        self.pattern = pattern
        self.socket = None
        self.subprocess = None
        if self.server != '':
            self.socket = Socket(self.server, self.port)
        else:
            self.subprocess = Subprocess(self.command)
        self.juman = Juman()
        #if self.rcfile != '' and self.server != '':
        #    sys.stderr.write("Warning: rcfile option may not work with Juman server.\n")
    def knp(self, sentence):
        self.parse(sentence)
    def parse(self, sentence):
        juman_lines = self.juman.juman_lines(sentence)
        juman_str = "%s\n%s\n" % ('\n'.join(juman_lines), self.pattern)
        if self.socket:
            knp_lines = self.socket.query(juman_str, pattern=self.pattern)
        else:
            knp_lines = self.subprocess.query(juman_str, pattern=self.pattern)
        return BList(knp_lines, self.pattern)

class KNPTest(unittest.TestCase):
    def setUp(self):
        self.knp = KNP()
    #def test_space(self):
        #result = self.knp.parse("「 」を含む文")
        #self.assertEqual(result.mrph_list()[1].midasi, '\ ')
    #def test_backslash(self):
        #result = self.knp.parse("「\」を含む文")
        #self.assertEqual(result.mrph[1].midasi, '\\')
    def test_dpnd(self):
        result = self.knp.parse("赤い花が咲いた。")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].parent.id, 1) 
        self.assertEqual(len(result[1].child), 1)
        self.assertEqual(result[1].child[0].id, 0)
        self.assertEqual(result[1].parent.id, 2)
        self.assertEqual(result[2].parent, None)
    def test_mrph(self):
        result = self.knp.parse("赤い花が咲いた。")
        self.assertEqual(''.join([m.midasi for m in result[0].mrph_list]), '赤い')
        self.assertEqual(''.join([m.midasi for m in result[1].mrph_list]), '花が')
        self.assertEqual(''.join([m.midasi for m in result[2].mrph_list]), '咲いた。')

if __name__ == '__main__':
    unittest.main()
