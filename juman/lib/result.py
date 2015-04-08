from mlist import MList
from morpheme import Morpheme

import re

def Result(result, pattern=r'^EOS$'):
    result_list = []
    if type(result) != list:
        for line in result.split("\n"):
            result_list.append("%s\n" % line)
    else:
        result_list = result
    mrphs = MList()
    for line in result_list:
        if re.match(pattern, line):
            break
        elif line.startswith("@ @ @"):
            mrphs.push_mrph(Morpheme(line, len(mrphs.mrph)))
        elif line.startswith("@"):
            mrphs.mrph[-1].push_doukei(Morpheme(line, len(mrphs.mrph)))
        else:
            mrphs.push_mrph(Morpheme(line, len(mrphs.mrph)))
    mrphs.set_readonly()
    return mrphs
