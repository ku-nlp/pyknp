.. pyknp documentation master file, created by
   sphinx-quickstart on Sat Aug 25 06:17:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=========================================
pyknp: Python Module for JUMAN++/KNP
=========================================

About
========================

形態素解析器JUMAN++(JUMAN)と構文解析器KNPのPythonバインディング (Python2系,3系の両方に対応)

Requirements
========================

- Python
    -  Verified Versions: 2.7.15,  3.5.6,  3.6.6.
- 形態素解析器 `JUMAN++`_ (JUMAN_)
    - JUMAN++はJUMANの後継となる形態素解析器
    - English pages of JUMAN++ (Japanese Morphological Analyzer): `EN_JUMAN++`_ (EN_JUMAN_)
- 構文解析器 KNP_
    - English page of KNP (Japanese Dependency and Case Structure Analyzer): EN_KNP_

.. _JUMAN++: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++
.. _JUMAN: http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN
.. _KNP: http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP
.. _EN_JUMAN++: http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN++
.. _EN_JUMAN: http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN
.. _EN_KNP: http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?KNP

Install pyknp
========================

.. code-block:: none

    % pip install pyknp

or

.. code-block:: none

    % git clone https://github.com/ku-nlp/pyknp
    % cd pyknp
    % python setup.py install [--prefix=path]



A Simple Explanation of JUMAN++/KNP
================================================

形態素解析器JUMAN++は文を形態素(Morpheme)単位に分割する。
構文解析器KNPでは文を3つの粒度、文節(Bunsetsu)、基本句(Tag)、形態素で扱い、
文節および基本句間の係り受け関係・格関係・照応関係を出力する。

各粒度による文分割の例:

.. code-block:: none

 下鴨神社の参道は暗かった。
   文節区切り:　 下鴨神社の|参道は|暗かった。
   基本句区切り: 下鴨|神社の|参道は|暗かった。
   形態素区切り: 下鴨|神社|の|参道|は|暗かった|。


係り受け解析・格解析の例:

.. code-block:: none

    下鴨神社の参道は暗かった。
    # S-ID:1 KNP:4.2-32bec061 DATE:2018/09/06 SCORE:-18.37446
    下鴨──┐　　　　　　　　　<体言>
          神社の──┐　　　　　<体言>
                  参道は──┐　<体言>
                      暗かった。<用言:形><格解析結果:ガ/参道;ト/->
    EOS


Usage
========================

| 詳しい使い方はこちらを参照してください。 :doc:`./usage`
| 関数やクラスの詳細は下記ドキュメントも参照してください。

**JUMAN++**

JUMAN++の実行例

.. code-block:: none

    % echo "下鴨神社の参道は暗かった。" | jumanpp
    下鴨 しもがも 下鴨 名詞 6 地名 4 * 0 * 0 "自動獲得:Wikipedia Wikipedia地名"
    神社 じんじゃ 神社 名詞 6 普通名詞 1 * 0 * 0 "代表表記:神社/じんじゃ ドメイン:文化・芸術 カテゴリ:場所-施設 地名末尾"
    の の の 助詞 9 接続助詞 3 * 0 * 0 NIL
    参道 さんどう 参道 名詞 6 普通名詞 1 * 0 * 0 "代表表記:参道/さんどう ドメイン:文化・芸術 カテゴリ:場所-施設"
    は は は 助詞 9 副助詞 2 * 0 * 0 NIL
    暗かった くらかった 暗い 形容詞 3 * 0 イ形容詞アウオ段 18 タ形 8 "代表表記:暗い/くらい"
    。 。 。 特殊 1 句点 1 * 0 * 0 NIL
    EOS

pyknpを用いた解析プログラム

.. code-block:: python

    --- example_juman.py ---
    # coding: utf-8
    from __future__ import unicode_literals # It is not necessary when you use python3.
    from pyknp import Juman
    jumanpp = Juman()   # default is JUMAN++: Juman(jumanpp=True). if you use JUMAN, use Juman(jumanpp=False)
    result = jumanpp.analysis("下鴨神社の参道は暗かった。")
    for mrph in result.mrph_list(): # 各形態素にアクセス
        print("見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))

プログラムの出力結果

.. code-block:: none

    % python3 example_juman.py
    見出し:下鴨, 読み:しもがも, 原形:下鴨, 品詞:名詞, 品詞細分類:地名, 活用型:*, 活用形:*, 意味情報:自動獲得:Wikipedia Wikipedia地名, 代表表記:
    見出し:神社, 読み:じんじゃ, 原形:神社, 品詞:名詞, 品詞細分類:普通名詞, 活用型:*, 活用形:*, 意味情報:代表表記:神社/じんじゃ ドメイン:文化・芸術 カテゴリ:場所-施設 地名末尾, 代表表記:神社/じんじゃ
    見出し:の, 読み:の, 原形:の, 品詞:助詞, 品詞細分類:接続助詞, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:
    見出し:参道, 読み:さんどう, 原形:参道, 品詞:名詞, 品詞細分類:普通名詞, 活用型:*, 活用形:*, 意味情報:代表表記:参道/さんどう ドメイン:文化・芸術 カテゴリ:場所-施設, 代表表記:参道/さんどう
    見出し:は, 読み:は, 原形:は, 品詞:助詞, 品詞細分類:副助詞, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:
    見出し:暗かった, 読み:くらかった, 原形:暗い, 品詞:形容詞, 品詞細分類:*, 活用型:イ形容詞アウオ段, 活用形:タ形, 意味情報:代表表記:暗い/くらい, 代表表記:暗い/くらい
    見出し:。, 読み:。, 原形:。, 品詞:特殊, 品詞細分類:句点, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:

**KNP**

| KNPの実行例。出力の読み方は次のURLを参照。
| `<http://cr.fvcrc.i.nagoya-u.ac.jp/~sasano/knp/format.html>`_

.. code-block:: none

    % echo "下鴨神社の参道は暗かった。" | jumanpp | knp -tab
    # S-ID:1 KNP:4.2-32bec061 DATE:2018/09/07 SCORE:-18.37446
    * 1D <SM-主体><SM-場所><SM-組織><BGH:神社/じんじゃ><文頭><地名><助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><正規化代表表記:下鴨/しもがも+神社/じんじゃ><主辞代表表記:神社/じんじゃ>
    + 1D <文節内><係:文節内><文頭><地名><体言><名詞項候補><先行詞候補><SM-場所><正規化代表表記:下鴨/しもがも>
    下鴨 しもがも 下鴨 名詞 6 地名 4 * 0 * 0 "自動獲得:Wikipedia Wikipedia地名 疑似代表表記 代表表記:下鴨/しもがも" <自動獲得:Wikipedia><Wikipedia地名><疑似代表表記><代表表記:下鴨/しもがも><正規化代表表記:下鴨/しもがも><漢字><かな漢字><名詞相当語><文頭><自立><内容語><タグ単位始><文節始><固有キー><用言表記末尾>
    + 2D <SM-主体><SM-場所><SM-組織><BGH:神社/じんじゃ><地名><助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:神社/じんじゃ><主辞代表表記:神社/じんじゃ>
    神社 じんじゃ 神社 名詞 6 普通名詞 1 * 0 * 0 "代表表記:神社/じんじゃ 地名末尾 カテゴリ:場所-施設 ドメイン:文化・芸術" <代表表記:神社/じんじゃ><地名末尾><カテゴリ:場所-施設><ドメイン:文化・芸術><正規化代表表記:神社/じんじゃ><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>
    の の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>
    * 2D <BGH:参道/さんどう><ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:参道/さんどう><主辞代表表記:参道/さんどう>
    + 3D <BGH:参道/さんどう><ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:参道/さんどう><主辞代表表記:参道/さんどう><解析格:ガ>
    参道 さんどう 参道 名詞 6 普通名詞 1 * 0 * 0 "代表表記:参道/さんどう カテゴリ:場所-施設 ドメイン:文化・芸術" <代表表記:参道/さんどう><カテゴリ:場所-施設><ドメイン:文化・芸術><正規化代表表記:参道/さんどう><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>
    は は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>
    * -1D <BGH:暗い/くらい><文末><時制-過去><句点><用言:形><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><状態述語><正規化代表表記:暗い/くらい><主辞代表表記:暗い/くらい>
    + -1D <BGH:暗い/くらい><文末><時制-過去><句点><用言:形><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><状態述語><正規化代表表記:暗い/くらい><主辞代表表記:暗い/くらい><用言代表表記:暗い/くらい><節-区切><節-主辞><主題格:一人称優位><格関係2:ガ:参道><格解析結果:暗い/くらい:形27:ガ/N/参道/2/0/1;ト/U/-/-/-/-><標準用言代表表記:暗い/くらい>
    暗かった くらかった 暗い 形容詞 3 * 0 イ形容詞アウオ段 18 タ形 8 "代表表記:暗い/くらい" <代表表記:暗い/くらい><正規化代表表記:暗い/くらい><かな漢字><活用語><表現文末><自立><内容語><タグ単位始><文節始><文節主辞><用言表記末尾>
    。 。 。 特殊 1 句点 1 * 0 * 0 NIL <英記号><記号><文末><付属>
    EOS

pyknpを用いた解析プログラム

.. code-block:: python

    --- example_knp.py ---
    # coding: utf-8
    from __future__ import unicode_literals # It is not necessary when you use python3.
    from pyknp import KNP
    knp = KNP()     # Default is JUMAN++. If you use JUMAN, use KNP(jumanpp=False)
    result = knp.parse("下鴨神社の参道は暗かった。")

    print("文節")
    for bnst in result.bnst_list(): # 各文節へのアクセス
        print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%d, 素性:%s" \
                % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring))

    print("基本句")
    for tag in result.tag_list(): # 各基本句へのアクセス
        print("\tID:%d, 見出し:%s, 係り受けタイプ:%s, 親基本句ID:%d, 素性:%s" \
                % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring))

    print("形態素")
    for mrph in result.mrph_list(): # 各形態素へのアクセス
        print("\tID:%d, 見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
                % (mrph.mrph_id, mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname))


プログラムの出力結果

.. code-block:: none

    % python3 example_knp.py
    文節
        ID:0, 見出し:下鴨神社の, 係り受けタイプ:D, 親文節ID:1, 素性:<SM-主体><SM-場所><SM-組織><BGH:神社/じんじゃ><文頭><地名><助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><正規化代表表記:下鴨/しもがも+神社/じんじゃ><主辞代表表記:神社/じんじゃ>
        ID:1, 見出し:参道は, 係り受けタイプ:D, 親文節ID:2, 素性:<BGH:参道/さんどう><ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:参道/さんどう><主辞代表表記:参道/さんどう>
        ID:2, 見出し:暗かった。, 係り受けタイプ:D, 親文節ID:-1, 素性:<BGH:暗い/くらい><文末><時制-過去><句点><用言:形><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><状態述語><正規化代表表記:暗い/くらい><主辞代表表記:暗い/くらい>
    基本句
        ID:0, 見出し:下鴨, 係り受けタイプ:D, 親基本句ID:1, 素性:<文節内><係:文節内><文頭><地名><体言><名詞項候補><先行詞候補><SM-場所><正規化代表表記:下鴨/しもがも>
        ID:1, 見出し:神社の, 係り受けタイプ:D, 親基本句ID:2, 素性:<SM-主体><SM-場所><SM-組織><BGH:神社/じんじゃ><地名><助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:神社/じんじゃ><主辞代表表記:神社/じんじゃ>
        ID:2, 見出し:参道は, 係り受けタイプ:D, 親基本句ID:3, 素性:<BGH:参道/さんどう><ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:参道/さんどう><主辞代表表記:参道/さんどう><解析格:ガ>
        ID:3, 見出し:暗かった。, 係り受けタイプ:D, 親基本句ID:-1, 素性:<BGH:暗い/くらい><文末><時制-過去><句点><用言:形><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><状態述語><正規化代表表記:暗い/くらい><主辞代表表記:暗い/くらい><用言代表表記:暗い/くらい><節-区切><節-主辞><主題格:一人称優位><格関係2:ガ:参道><格解析結果:暗い/くらい:形27:ガ/N/参道/2/0/1;ト/U/-/-/-/-><標準用言代表表記:暗い/くらい>
    形態素
        ID:0, 見出し:下鴨, 読み:しもがも, 原形:下鴨, 品詞:名詞, 品詞細分類:地名, 活用型:*, 活用形:*, 意味情報:自動獲得:Wikipedia Wikipedia地名 疑似代表表記 代表表記:下鴨/しもがも, 代表表記:下鴨/しもがも
        ID:1, 見出し:神社, 読み:じんじゃ, 原形:神社, 品詞:名詞, 品詞細分類:普通名詞, 活用型:*, 活用形:*, 意味情報:代表表記:神社/じんじゃ 地名末尾 カテゴリ:場所-施設 ドメイン:文化・芸術, 代表表記:神社/じんじゃ
        ID:2, 見出し:の, 読み:の, 原形:の, 品詞:助詞, 品詞細分類:接続助詞, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:
        ID:3, 見出し:参道, 読み:さんどう, 原形:参道, 品詞:名詞, 品詞細分類:普通名詞, 活用型:*, 活用形:*, 意味情報:代表表記:参道/さんどう カテゴリ:場所-施設 ドメイン:文化・芸術, 代表表記:参道/さんどう
        ID:4, 見出し:は, 読み:は, 原形:は, 品詞:助詞, 品詞細分類:副助詞, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:
        ID:5, 見出し:暗かった, 読み:くらかった, 原形:暗い, 品詞:形容詞, 品詞細分類:*, 活用型:イ形容詞アウオ段, 活用形:タ形, 意味情報:代表表記:暗い/くらい, 代表表記:暗い/くらい
        ID:6, 見出し:。, 読み:。, 原形:。, 品詞:特殊, 品詞細分類:句点, 活用型:*, 活用形:*, 意味情報:NIL, 代表表記:

**Python2系の場合**

pyknpではすべての入出力でUnicodeを想定しており、それ以外の文字コードによる入力はエラーとなる。
そのためPython2系では、上記のプログラム冒頭の下記の2行が必要である。

.. code-block:: python

    # coding: utf-8
    from __future__ import unicode_literals


Documents
============
.. toctree::
   :maxdepth: 2

   pyknp.juman
   pyknp.knp


Author/Contact
========================
京都大学 黒橋・河原研究室 (contact@nlp.ist.i.kyoto-u.ac.jp)

- John Richardson, Tomohide Shibata, Yuta Hayashibe, Tomohiro Sakaguchi


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

