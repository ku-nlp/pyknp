# pyknp: Python Module for KNP/JUMAN Version 0.1

- Kurohashi-Kawahara Lab, Kyoto University
- Written by 
    - [John Richardson](john@nlp.ist.i.kyoto-u.ac.jp)
    - [Tomohide Shibata](shibata@i.kyoto-u.ac.jp)
    - [Yuta Hayashibe](yuta-h@i.kyoto-u.ac.jp)

## INSTALLATION

python setup.py install [--prefix=path]

## USAGE

The usage of pyknp is designed to be as similar as possible to the official
Perl module. Please check the code and the Perl module documentation for further
information.

JUMAN and KNP can be invoked by making an instance of the classes Juman and KNP
respectively. By default, JUMAN/KNP will be called as a subprocess from the
binaries juman/knp found in the PATH environment variable. Specifying
server=HOSTNAME and port=NUMBER in the constructor will switch to server mode,
where JUMAN/KNP is queried as a server run using the -S option.

The methods juman.analysis('sentence') and knp.parse('sentence') return a list
of morphemes (MList) and bunsetsu (BList) respectively, containing Morpheme and
Bunsetsu objects. To read already parsed data from a file, use
juman.result('data') or knp.result('data').

Morphemes contain the following:
    mrph_id (= id in Perl module), midasi, yomi, genkei, hinsi, hinsi_id,
    bunrui, bunrui_id, katuyou1, katuyou1_id, katuyou2, katuyou2_id, imis,
    fstring

Bunsetsu contain the following:
    mrph_list (list of Morphemes), tag_list (list of Tags), parent_id (ID of
    parent bunsetsu), parent (parent bunsetsu), children (child bunsetsu, = child in Perl module),
    dpndtype, fstring (feature string), bnst_id (= id in Perl module) 

Tags contain the following:
    mrph_list (list of Morphemes), parent_id, parent, children,
    dpndtype, fstring (feature string), tag_id (= id in Perl module)

Note that the pyknp module expects all input/output to be in Unicode, not any
encoding such as UTF-8. Queries are sent to JUMAN/KNP after converting
internally to UTF-8.

## EXAMPLE

### Juman
    #-*- encoding: utf-8 -*-
    from pyknp import Juman
    import sys
    import codecs
    sys.stdin = codecs.getreader('utf_8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    
    # Use Juman in subprocess mode
    juman = Juman()
    result = juman.analysis(u"これはペンです。")
    print ','.join(mrph.midasi for mrph in result)
    
    for mrph in result.mrph_list():
        print u"見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
        % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname)
    
    # Use Juman in server mode
    juman = Juman(server='localhost', port=12345)
    ...

#### Read from file
    data = ""
    with open("result.juman") as file_in:
        for line in file_in:
            data += line.decode('utf-8')
            if line.strip() == "EOS":
                result = juman.result(data)
                print ",".join(mrph.genkei for mrph in result.mrph_list())
                data = ""

### KNP
    #-*- encoding: utf-8 -*-
    from pyknp import KNP
    import sys
    import codecs
    sys.stdin = codecs.getreader('utf_8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    
    # Use KNP in subprocess mode
    knp = KNP()
    # if you don't need case analysis
    # knp = KNP(option='-dpnd -tab')
    result = knp.parse(u"京都大学に行った。")
    
    # loop for bunsetsu
    for bnst in result.bnst_list():
        print u"ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
        % (bnst.bnst_id, "".join(mrph.midasi for mrph in bnst.mrph_list()), bnst.dpndtype, bnst.parent_id, bnst.fstring)
    
    # loop for tag (kihonku, basic phrase)
    for tag in result.tag_list():
        print u"ID:%s, 見出し:%s, 係り受けタイプ:%s, 親文節ID:%s, 素性:%s" \
        % (tag.tag_id, "".join(mrph.midasi for mrph in tag.mrph_list()), tag.dpndtype, tag.parent_id, tag.fstring)
    
    # loop for mrph
    for mrph in result.mrph_list():
        print u"見出し:%s, 読み:%s, 原形:%s, 品詞:%s, 品詞細分類:%s, 活用型:%s, 活用形:%s, 意味情報:%s, 代表表記:%s" \
        % (mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui, mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname)

#### Read from file
    data = ""
    with open("result.knp") as file_in:
        for line in file_in:
            data += line.decode('utf-8')
            if line.strip() == "EOS":
                result = knp.result(data)
                print ",".join(mrph.genkei for mrph in result.mrph_list())
                data = ""
