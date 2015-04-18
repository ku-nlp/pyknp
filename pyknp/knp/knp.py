#-*- encoding: utf-8 -*-

from pyknp import Juman
from pyknp import Socket, Subprocess  # TODO(john): move to separate file
from pyknp import BList
import unittest

VERSION = '0.4.9'

class KNP(object):
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
        #    sys.stderr.write(
        #           "Warning: rcfile option may not work with Juman server.\n")
    def knp(self, sentence):
        self.parse(sentence)
    def parse(self, sentence):
        assert(isinstance(sentence, unicode))
        juman_lines = self.juman.juman_lines(sentence)
        juman_str = "%s%s" % (juman_lines, self.pattern)
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
        result = self.knp.parse(u"赤い花が咲いた。")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].parent.bnst_id, 1)
        self.assertEqual(len(result[1].child), 1)
        self.assertEqual(result[1].child[0].bnst_id, 0)
        self.assertEqual(result[1].parent.bnst_id, 2)
        self.assertEqual(result[2].parent, None)
    def test_mrph(self):
        result = self.knp.parse(u"赤い花が咲いた。")
        self.assertEqual(''.join([mrph.midasi for mrph in result[0].mrph_list]), u'赤い')
        self.assertEqual(''.join([mrph.midasi for mrph in result[1].mrph_list]), u'花が')
        self.assertEqual(''.join([mrph.midasi for mrph in result[2].mrph_list]), u'咲いた。')

if __name__ == '__main__':
    unittest.main()
