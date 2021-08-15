#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs
import sys

import pyknp
import six

if six.PY2:
    sys.stdin = codecs.getreader('UTF-8')(sys.stdin)
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
    sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)


def draw_tree(bl, outf):
    assert isinstance(bl, pyknp.BList)

    tl = pyknp.TList()
    tags = bl.tag_list()
    for tag in tags:
        tl.push_tag(tag)
    nodelines = tl.sprint_tree().split(u"\n")[:-1]

    outf.write(u"# S-ID: %s\n" % bl.sid)

    for i, nl in enumerate(nodelines):
        outf.write(nl)
        outf.write(u"\t")
        outf.write(u"/ ")
        pas = tags[i].features.pas
        if pas is not None:
            outf.write(pas.cfid)
            outf.write(u"\t")
            for casename, arglist in sorted(pas.arguments.items()):
                for arg in arglist:
                    if arg.sid == bl.sid:
                        if hasattr(tags[arg.tid], 'head_prime_repname') \
                                and tags[arg.tid].head_prime_repname:
                            rep = tags[arg.tid].head_prime_repname
                        else:
                            rep = tags[arg.tid].repname
                    else:
                        rep = u"<sid=%s,tid=%s>" % (arg.sid, arg.tid)
                    outf.write(u"%s:%s " % (casename, rep))

        outf.write(u"/ ")
        rels = tags[i].features.rels
        if rels is not None:
            for rel in sorted(rels, key=lambda x: x.atype):
                outf.write(u"%s:%s " % (rel.atype, rel.target))
        outf.write(u"\n")

    outf.write(u"\n")


def draw_trees(inf, outf, lattice_format):
    juman_format = pyknp.JUMAN_FORMAT.DEFAULT
    if lattice_format:
        juman_format = pyknp.JUMAN_FORMAT.LATTICE_TOP_ONE
    lines = []
    for line in inf:
        lines.append(line)
        if line == u"EOS\n":
            bl = pyknp.BList(u"".join(lines), juman_format=juman_format)
            draw_tree(bl, outf)
            lines = []


def main():
    epilog = '''
             try:
             `echo これはテストです。 | jumanpp |
             knp -tab -anaphora | knp-drawtree`
             '''
    parser = argparse.ArgumentParser(
        prog='knp-drawtree',
        description='draw a parse tree from output of knp command',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=epilog)
    parser.add_argument("-i", "--input", default="-",
                         help="input source")
    parser.add_argument("-o", "--output", default="-",
                         help="output destination")
    parser.add_argument("-L", "--lattice_format", action="store_true",
                         help="output in lattice format")

    args = parser.parse_args()

    if args.input == "-":
        inf = sys.stdin
    else:
        inf = codecs.open(args.input, "r", "utf8")

    if args.output == "-":
        outf = sys.stdout
    else:
        outf = codecs.open(args.output, "w", "utf8")
    draw_trees(inf, outf, args.lattice_format)


if __name__ == '__main__':
    main()
