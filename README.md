# pyknp: Python Module for KNP/JUMAN++

- 形態素解析器JUMAN++(JUMAN)と構文解析器KNPのPythonバインディングです (Python2と3の両方に対応)。
- 京都大学 黒橋・河原研究室 (contact@nlp.ist.i.kyoto-u.ac.jp)
- 著者:
    - [John Richardson](john@nlp.ist.i.kyoto-u.ac.jp)
    - [Tomohide Shibata](shibata@i.kyoto-u.ac.jp)
    - [Yuta Hayashibe](yuta-h@i.kyoto-u.ac.jp)
- See README-en.md for English README.

## インストール
予めインストールする必要のあるプログラム
- JUMAN++ (JUMAN) http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++ (http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN)
- KNP http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP

pyknpのインストール:
```
python setup.py install [--prefix=path]
```

## 構成

#### JUMAN++/KNPの扱う言語情報単位について
JUMAN++/KNPでは文を3つの粒度、形態素(Morpheme)、基本句(Tag)、文節(Bunsetsu)で扱う。
```
例: 「京都大学へ行く」
  形態素区切り: |京都|大学|へ|行く|
  基本句区切り: |京都|大学へ|行く|
  文節区切り:   |京都大学へ|行く|
```
形態素解析器JUMAN++は文を形態素単位に分割する。
構文解析器KNPはJUMAN++の解析結果を入力とし、
文節および基本句間の係り受け関係・格関係・照応関係を出力する。


#### pyknpの構造
pyknpでは、JUMAN++/KNPにより解析された情報を形態素/基本句/文節オブジェクトとして管理する。
各オブジェクトからは、より粒度の小さいオブジェクトにアクセスすることができる。

以下に形態素/基本句/文節オブジェクトのもつ情報を記す。
- 形態素オブジェクトの保持する情報:  
    形態素ID(mrph_id), 見出し(midasi), 読み(yomi), 原形(genkei), 品詞(hinsi), 品詞ID(hinsi_id),
    品詞細分類(bunrui), 品詞細分類ID(bunrui_id), 活用型(katuyou1), 活用型ID(katuyou1_id), 
    活用形(katuyou2), 活用形ID(katuyou2_id), 意味情報(imis), 代表表記(repname), その他の情報(fstring)

- 基本句オブジェクトの保持する情報:  
    形態素オブジェクトのリスト(mrph_list), 基本句ID(tag_id),
    親基本句ID(parent_id), 親基本句オブジェクト(parent), 
    子基本句オブジェクトのリスト(children),
    係り受けタイプ(dpndtype), その他の情報(fstring)

- 文節オブジェクトの保持する情報:  
    形態素オブジェクトのリスト(mrph_list), 基本句オブジェクトのリスト(tag_list), 
    文節ID(bnst_id), 親文節ID(parent_id), 親文節オブジェクト(parent), 子文節オブジェクトのリスト(children),
    係り受けタイプ(dpndtype: D:dependency, P:parallel, I:incomplete parallel, A:apposition), 
    その他の情報(fstring)

#### Python2系を用いる場合の注意点
pyknpでは、すべての入出力でUnicodeを想定しており、それ以外の文字コードによる入力はエラーとなる。




## 使い方
### JUMAN++
###### pyknp内でJUMAN/JUMAN++の実行する場合  
    #-*- encoding: utf-8 -*-
    from pyknp import Juman

    ### Python2系の場合、次の4行のコメントを外す。KNPの場合も同様。
    #import sys
    #import codecs
    #sys.stdin = codecs.getreader('utf_8')(sys.stdin)
    #sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    
    ### JUMANインスタンスを作成する
    # JUMANを使う場合: juman = Juman(juman=True)
    # JUMANPPをサーバモードで利用する場合: jumanpp = Juman(server='localhost', port=12345)
    jumanpp = Juman()   

    ### 文を解析し、解析結果を Python の内部構造に変換して result に格納する
    result = jumanpp.analysis(u"これはペンです。")  
    print ','.join(mrph.midasi for mrph in result)
    
    for mrph in result.mrph_list(): # 各形態素にアクセス
        print u"見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
        % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname)

###### Read from file
    data = ""
    with open("result.juman") as file_in:
        for line in file_in:
            data += line.decode
            if line.strip() == "EOS":
                result = juman.result(data)
                print ",".join(mrph.genkei for mrph in result.mrph_list())
                data = ""

### KNP
###### pyknp内でKNPの実行する場合  
    #-*- encoding: utf-8 -*-
    from pyknp import KNP
    
    ### KNPインスタンスを作成する
    # JUMANを使う場合: knp = KNP(juman=True)
    # 格解析を行わず構文解析のみ行う場合は knp = KNP(option='-dpnd -tab') とすると30倍速くなる
    knp = KNP()     
    result = knp.parse(u"京都大学に行った。")
    
    ### 各文節へのアクセス
    for bnst in result.bnst_list():
        print u"ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
        % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring)
    
    ### 各基本句へのアクセス
    for tag in result.tag_list():
        print u"ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
        % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring)
    
    ### 各形態素へのアクセス
    for mrph in result.mrph_list():
        print u"見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
        % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname)


###### 予め準備したKNP解析結果ファイルを利用する場合
    data = ""
    with open("result.knp") as file_in:
        for line in file_in:
            data += line
            if line.strip() == "EOS":
                result = knp.result(data)
                print ",".join(mrph.genkei for mrph in result.mrph_list())
                data = ""


