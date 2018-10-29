# pyknp: Python Module for JUMAN++/KNP

形態素解析器JUMAN++(JUMAN)と構文解析器KNPのPythonバインディング (Python2系と3系の両方に対応)。

## Requirements
- Python 
    - Verified Versions: 2.7.15,  3.5.6,  3.6.6.
- 形態素解析器 [JUMAN++](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++) [[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN++)]
(or [JUMAN](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN)[[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN)])
    - JUMAN++ はJUMANの後継にあたる形態素解析器
- 構文解析器 [KNP](http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP) [[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?KNP)]

## Installation
```
% pip install pyknp
```

or 

```
% git clone https://github.com/ku-nlp/pyknp
% cd pyknp
% python setup.py install [--prefix=path]
```

## Documents
https://pyknp.readthedocs.io/en/latest/


## Authors/Contact
京都大学 黒橋・河原研究室 (contact@nlp.ist.i.kyoto-u.ac.jp)
- John Richardson, Tomohide Shibata, Yuta Hayashibe, Tomohiro Sakaguchi
