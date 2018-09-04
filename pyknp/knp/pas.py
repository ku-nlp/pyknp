#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import collections
import six

import sys

class Argument(object):
    """ 項に関する情報を保持するオブジェクト 

    詳しくは下記ページの「格要素側」の記述方法を参照
    http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP%2F%E6%A0%BC%E8%A7%A3%E6%9E%90%E7%B5%90%E6%9E%9C%E6%9B%B8%E5%BC%8F

    Attributes:
        sid (str): 文ID
        tid (int): 基本句ID
        eid (int): Entity ID
        rep (str): 表記
        flag (str): フラグ (C, N, O, D, E, U)
        sdist (int): 述語の何文前か
    """
    def __init__(self, sid=None, tid=None, eid=None, rep='', flag=None, sdist=None):
        assert isinstance(tid, int)
        assert isinstance(rep, six.text_type)
        self.sid = sid
        self.tid = tid
        self.eid = eid
        self.rep = rep
        self.flag = flag
        self.sdist = sdist 

ArgRepname = collections.namedtuple("ArgRepname", "repname,tid_list")


class Pas(object):
    """
    述語項構造を扱うクラス
    文をまたがる述語項構造は非対応

    Usage:
        result = knp.result(knp_result)
        pas = Pas(5, result)

    Attributes:
        arguments (dict of (case, list of Argument)): 
                 格と項を対応付けた辞書 {case: [Argument, ..]}
                 keyは格を表す文字列, valueはArgumentオブジェクトのリスト。
                 リスト形式なのは、ガ格などは複数の項を取り得るため。
    """
    def __init__(self, tid=None, result=None, knpstyle=True):
        self.valid = True
        self.cfid = None 
        self.arguments = collections.defaultdict(list)
         
        if tid is None:
            self.valid = False
            return
            
        self.tid = tid
        self.tag_list = result.tag_list()

        pas_analysis = self.tag_list[self.tid].features.get(u"述語項構造") # -anaphoraの場合
        if pas_analysis is not None:
            self.__parse_case_analysis(pas_analysis, pasFlag=True)

        case_analysis = self.tag_list[self.tid].features.get(u"格解析結果")
        if(case_analysis is None):
            self.valid = False
            return
        self.__parse_case_analysis(case_analysis)
        return
    
    def is_valid(self):
        return self.valid
   
    # TODO: 代表表記系列か 正規化代表表記 の両系統に対応する必要がある
    def get_predicate_repname(self):
        """
        基本句の代表表記を返す
        "道を歩き回ってた" -> 歩く/あるく
        """
        if(self.is_valid()):
            return self.tag_list[self.tid].repname
        else:
            return None
    
    def get_predicate_declinable_repname(self):
        """
        基本句の用言代表表記を返す
        "道を歩き回ってた" -> 歩く/あるく+回る/まわる~テ形+る/る
        """
        if(self.is_valid()):
            return self.tag_list[self.tid].repname
        else:
            return None
        return self.tag_list[self.tid].features.get(u"用言代表表記")
    
    def get_short_predicate(self): # alias
        return self.get_predicate_repname()
    
    def get_long_predicate(self): # alias
        return self.get_predicate_declinable_repname()
     
    def get_arguments(self,case):
        """
        指定した格の各項ごとに代表表記の配列を返す
        """
        output = []
        for arg in self.arguments[case]:
            tid = arg.tid
            rep = self.tag_list[tid].repname
            output.append(ArgRepname("+".join(rep), tid)) 
        return output
    
    def get_long_arguments(self, case):
        """
        項の主辞’代表表記相当の表記と項が含まれる基本句idリストのタプルを返す．
         
        項の主辞’代表表記相当を与える．=> 項の主辞'代表表記があれば取り出す
        主辞が一文字漢字であり，直前が名詞の場合は，その直前の基本句を連結した表記を返す．
        格に対して項は複数存在しうるので，戻り値は配列を渡す．
        
        Usage:
            self.get_long_arguments(ガ) 
            > [ ("研究/けんきゅう+者/しゃ", [1,2]) ]
        """
        output = []
            
        for arg in self.arguments[case]:
            tids = [arg.tid]
            long_rep = []
            if(u"一文字漢字" in self.tag_list[arg.tid].features 
                    and arg.tid > 0 
                    and self.tag_list[arg.tid-1].mrph_list()[-1].hinsi in ["名詞","接頭辞"]):
                tids.insert(0, arg.tid-1)

            long_argument = ""
            if(u"主辞’代表表記" in self.tag_list[arg.tid].features and
                self.tag_list[arg.tid].features[u"主辞’代表表記"] is not None and
                len(self.tag_list[arg.tid].features[u"主辞’代表表記"]) > 0 ):
                long_argument = self.tag_list[arg.tid].features[u"主辞’代表表記"]
            else: 
                for tid in tids:
                    long_rep.append(self.tag_list[tid].repname)
                long_argument = "+".join(long_rep)
            output.append(ArgRepname(long_argument,tids)) 
        return output
     
    def get_orig_result(self):
        return self.tag_list[self.tid].features.get(u"格解析結果")
     
    def __parse_case_analysis(self, analysis_result, pasFlag=False):
        assert isinstance(analysis_result, six.text_type)
        c0 = analysis_result.find(u':')
        c1 = analysis_result.find(u':', c0 + 1)
        self.cfid = analysis_result[:c0] + u":" + analysis_result[c0 + 1:c1]
        
        if analysis_result.count(u":") < 2:  # For copula
            self.valid = False
            return
        
        for k in analysis_result[c1 + 1:].split(u';'):
            items = k.split(u"/")
            caseflag = items[1]
            if caseflag == u"U" or caseflag == u"-":
                continue
            
            if pasFlag: # anaphora
                mycase = items[0]
                rep = items[2]
                sdist = int(items[3])
                tid = int(items[4])
                eid = int(items[5])
                arg = Argument(sdist=sdist, tid=tid, eid=eid, rep=rep, flag=caseflag)
                self.arguments[mycase].append(arg)
            else:
                mycase = items[0]
                rep = items[2]
                tid = int(items[3])
                sdist = int(items[4])
                sid = items[5]
               
                arg = Argument(sid=sid, tid=tid, rep=rep, flag=caseflag, sdist=sdist)
                self.arguments[mycase].append(arg)


