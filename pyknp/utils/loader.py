#-*- encoding: utf-8 -*-
from pyknp import JUMAN_FORMAT
from pyknp import Juman, KNP


def load_juman_from_stream(f, juman_format=JUMAN_FORMAT.DEFAULT):
    """
    JUMANフォーマットの解析結果ファイルを解釈し、文節列オブジェクトを返す

    Args:
        f (file): JUMANフォーマットの解析結果のファイルオブジェクト
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

    Yields:
        MList: 形態素列オブジェクト
    """
    juman = Juman()
    buf = ""
    for line in f:
        buf += line
        if line.startswith("EOS"):
            yield juman.result(buf, juman_format=juman_format)
            buf = ""


def load_knp_from_stream(f, juman_format=JUMAN_FORMAT.DEFAULT):
    """
    KNPフォーマットの解析結果ファイルを解釈し、文節列オブジェクトを返す

    Args:
        f (file): KNPフォーマットの解析結果のファイルオブジェクト
        juman_format (JUMAN_FORMAT): Jumanのlattice出力形式

    Yields:
        BList: 文節列オブジェクト
    """
    knp = KNP()
    buf = ""
    for line in f:
        buf += line
        if line.startswith("EOS"):
            yield knp.result(buf, juman_format=juman_format)
            buf = ""
