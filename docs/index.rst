.. pyknp documentation master file, created by
   sphinx-quickstart on Sat Aug 25 06:17:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========================================
pyknp: Python Module for KNP/JUMAN++
=========================================

About
============

- 形態素解析器JUMAN++(JUMAN)と構文解析器KNPのPythonバインディング (Python2と3の両方に対応)
- 京都大学 黒橋・河原研究室 (contact@nlp.ist.i.kyoto-u.ac.jp)

Installation
============

予めインストールする必要のあるプログラム

- 形態素解析器 `JUMAN++`_ (JUMAN_)
- 構文解析器 KNP_

.. _JUMAN++: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
.. _JUMAN: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN
.. _KNP: http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP

pyknpのインストール

.. code-block:: none

   python setup.py install [--prefix=path]



Usage
============

JUMAN++/KNPでは文を3つの粒度、形態素(Morpheme)、基本句(Tag)、文節(Bunsetsu)で扱う。

例: 「京都大学へ行く」
  | 形態素区切り: 京都|大学|へ|行く
  | 基本句区切り: 京都|大学へ|行く
  | 文節区切り:   京都大学へ|行く

形態素解析器JUMAN++は文を形態素単位に分割する。
構文解析器KNPはJUMAN++の解析結果を入力とし、
文節および基本句間の係り受け関係・格関係・照応関係を出力する。


JUMAN++

.. code-block:: python

    from pyknp import Juman
    jumanpp = Juman()   
    result = jumanpp.analysis("これはペンです。")  
    for mrph in result.mrph_list(): # 各形態素にアクセス
        print("見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))


KNP

.. code-block:: python

    from pyknp import KNP
    knp = KNP()     
    result = knp.parse("京都大学に行った。")
    
    for bnst in result.bnst_list(): # 各文節へのアクセス
        print("ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
                % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring))
    
    for tag in result.tag_list(): # 各基本句へのアクセス
        print("ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
                % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring))
    
    for mrph in result.mrph_list(): # 各形態素へのアクセス
        print("見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))

詳しくはこちら。


Documents
============
.. toctree::
   :maxdepth: 2

   pyknp.juman
   pyknp.knp


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
