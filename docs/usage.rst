Usage Deatails and Tips
========================================

予め準備したJUMAN/KNP解析結果ファイルを利用する方法
------------------------------------------------------------------------------------------------

JUMAN++やKNPは決して速くないため、大量のテキストを解析する際は
juman.analysis関数やknp.parse関数を用いて実行のたびに形態素解析や構文解析を行うのではなく、
予めJUMAN++/KNPを適用した解析済みファイルを用意しこれを読み込む方が良い。

Juman/KNPオブジェクトのresult関数に1文ずつの解析結果を渡すことで、読み込むことができる。

JUMAN++

.. code-block:: python

    --- read_juman_results.py ---
    from pyknp import Juman
    juman = Juman()
    data = ""
    with open("sample.juman") as file_in:
        for line in file_in:
            data += line
            if line.strip() == "EOS":
                result = juman.result(data)
                print(",".join(mrph.genkei for mrph in result.mrph_list()))
                data = ""

.. code-block:: none

    % echo "下鴨神社の参道は暗かった。" | jumanpp > sample.juman
    % python3 read_juman_results.py
    下鴨,神社,の,参道,は,暗い,。


KNP

.. code-block:: python

    --- read_knp_results.py ---
    from pyknp import KNP
    knp = KNP()
    data = ""
    with open("sample.knp") as file_in:
        for line in file_in:
            data += line
            if line.strip() == "EOS":
                result = knp.result(data)
                print(",".join(mrph.genkei for mrph in result.mrph_list()))
                data = ""

.. code-block:: none

    % echo "下鴨神社の参道は暗かった。" | jumanpp | knp -tab > sample.knp 
    % python3 read_knp_results.py
    下鴨,神社,の,参道,は,暗い,。



係り受け情報を取得する方法
------------------------------------------------

係り受け関係は木構造をなす。

- bnst.parent は親文節を返す。ただし一番後ろの文節は親文節を持たないので None が返る。

- bnst.children は子文節のリストを返す。子が一つもない (空リスト) こともあるし、複数の場合もある。

以下のコードは各係り受け関係を矢印 -> でつないでプリントする


.. code-block:: python

    --- dpnd.py ---
    from pyknp import KNP

    knp = KNP()
    result = knp.parse("望遠鏡で泳いでいる少女を見た。")

    for bnst in result.bnst_list():
        parent = bnst.parent
        if parent is not None:
            child_rep = " ".join(mrph.repname for mrph in bnst.mrph_list())
            parent_rep = " ".join(mrph.repname for mrph in parent.mrph_list())
            print(child_rep, "->", parent_rep)

.. code-block:: none

    % python3 tests/dpnd.py
    望遠/ぼうえん 鏡/かがみ  -> 見る/みる
    泳ぐ/およぐ いる/いる -> 少女/しょうじょ
    少女/しょうじょ  -> 見る/みる



述語項構造情報を取得する方法
------------------------------------------------

述語項構造とは、何がどうした、という述語とその項からなる構造のことである。
KNPにおいて述語項構造情報は、基本句レベルの情報として保持される。
pyknpではTagクラスのpasオブジェクトがこの情報を保持しており、
述語の基本句ではPasオブジェクト、その他の基本区ではNoneを指す。

Pasオブジェクトは、該当述語の述語と項の情報を管理する。
Pasオブジェクト中のargumentsオブジェクトは、{格: Argumentオブジェクトのリスト}
という辞書である。Argumentオブジェクトは項の情報を管理する。
格と項の情報が1対1対応でないのは、ガ格などが複数の項を取り得るためである。

Pas, Argument クラスの詳細は下記ドキュメントの `Pas module` の項目を参照してほしい。
:doc:`./tag`

下記は文中の述語と項を取り出すサンプルプログラムである。

.. code-block:: python

    --- get_pas.py ---
    from pyknp import KNP

    knp = KNP()
    result = knp.parse("望遠鏡で泳いでいる少女を見た。")

    for tag in result.tag_list():
        if tag.pas is not None: # find predicate
            print('述語: %s' % ''.join(mrph.midasi for mrph in tag.mrph_list()))
            for case, args in tag.pas.arguments.items(): # case: str, args: list of Argument class
                for arg in args: # arg: Argument class
                    print('\t格: %s,  項: %s  (項の基本句ID: %d)' % (case, arg.midasi, arg.tid))

.. code-block:: none

    % python3 get_pas.py
    述語: 泳いでいる
        格: ガ,  項: 少女  (項の基本句ID: 3)
    述語: 見た。
        格: ヲ,  項: 少女  (項の基本句ID: 3)
        格: デ,  項: 鏡  (項の基本句ID: 1)
