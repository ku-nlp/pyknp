# pyknp: Python Module for KNP/JUMAN Version 0.1

- Written by John Richardson
- Kurohashi-Kawahara Lab, Kyoto University
- john@nlp.ist.i.kyoto-u.ac.jp

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
    parent bunsetsu), parent (parent bunsetsu), child (child bunsetsu),
    dpndtype, fstring (feature string), bnst_id (= id in Perl module) 

Tags contain the following:
    mrph_list (list of Morphemes), parent_id, dpndtype, fstring (feature
    string), tag_id (= id in Perl module)

Note that the pyknp module expects all input/output to be in Unicode, not any
encoding such as UTF-8. Queries are sent to JUMAN/KNP after converting
internally to UTF-8.

## EXAMPLE

    #-*- encoding: utf-8 -*-
    
    from pyknp import Juman
    from pyknp import KNP
    
    # Use KNP in subprocess mode
    knp = KNP()
    result = knp.parse(u"赤い花が咲いた。")
    print ','.join(mrph.midasi for mrph in result.mrph_list())
    
    # Use JUMAN in server mode
    juman = Juman(server='localhost', port=12345)
    result = juman.analysis(u"これはペンです。")
    print ','.join(mrph.genkei for mrph in result)
    
    # Read from file
    data = ""
    with open("result.juman") as file_in:
        for line in file_in:
            data += line.decode('utf-8')
            if line.strip() == "EOS":
                result = juman.result(data)
                print ",".join(mrph.genkei for mrph in result)
                data = ""