#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
import collections
import six
import re


class Argument(object):
    """ 項に関する情報を保持するオブジェクト 

    詳しくは下記ページの「格要素側」の記述方法を参照
    http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP%2F%E6%A0%BC%E8%A7%A3%E6%9E%90%E7%B5%90%E6%9E%9C%E6%9B%B8%E5%BC%8F

    Attributes:
        sid (str): 文ID
        tid (int): 基本句ID
        eid (int): Entity ID
        midasi (str): 表記
        flag (str): フラグ (C, N, O, D, E, U)
        sdist (int): 述語の何文前か
    """
    def __init__(self, sid=None, tid=None, eid=None, midasi='', flag=None, sdist=None):
        assert isinstance(tid, int)
        assert isinstance(midasi, six.text_type)
        self.sid = sid
        self.tid = tid
        self.eid = eid
        self.midasi = midasi
        self.flag = flag
        self.sdist = sdist 


ArgRepname = collections.namedtuple("ArgRepname", "repname,tid_list")


class CaseInfoFormat(object): 
    """ 格/述語項構造のフォーマットを管理する名前空間 """
    CASE = 0  # 格解析フォーマット
    PASv41 = 1  # KNP v4.1 での述語項構造フォーマット
    PASv42 = 2  # KNP v4.2 での述語項構造フォーマット


class Pas(object):
    """ 述語項構造を扱うクラス

    Usage:
        result = knp.result(knp_result)
        pas = result.tag_list()[tid].pas # tid番目の基本句(述語)の項構造

    Attributes:
        cfid (str): 格フレームID (例: "行う/おこなう:動10")
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
        self.tid2sdist = {}
        self.sid = result.sid
        tag_predicate = self.tag_list[self.tid]

        if "項構造" in tag_predicate.features:  # KNP v4.1 で -anaphora
            # (eid, tid, sdist) の対を記録し、dictに保持(eid2tid, tid2sdist)
            # eid2tidはeidのエンティティが初出のTag位置(tid)を保持
            self.eid2tid = {}
            for tag in self.tag_list:
                if 'EID' in tag.features:
                    eid = int(tag.features['EID'])
                    self.eid2tid[eid] = tag.tag_id
            # (tid, sdist) を記録するため、"格解析結果"の値をパース
            case_analysis = tag_predicate.features.get("格解析結果")
            for items in self.__parse_case_analysis_items(case_analysis, CaseInfoFormat.CASE):
                (mycase, caseflag, midasi, eid, tid, sdist, sid) = items
                self.tid2sdist[tid] = sdist
            self.__set_args(tag_predicate.features.get("項構造"), CaseInfoFormat.PASv41)

        elif "述語項構造" in tag_predicate.features:  # KNP v4.2 (unpublished) で -anaphora
            self.__set_args(tag_predicate.features.get("述語項構造"), CaseInfoFormat.PASv42)

        elif "格解析結果" in tag_predicate.features: 
            self.__set_args(tag_predicate.features.get("格解析結果"), CaseInfoFormat.CASE)

        else:
            self.valid = False
    
    def is_valid(self):
        return self.valid
   
    def get_arguments(self, case):
        """
        指定した格の各項ごとに代表表記の配列を返す

        Usage:
            result = knp.parse("研究者になる")
            print(result.tag_list()[2].midasi)
            >> なる
            print(result.tag_list()[2].pas.get_arguments("ニ"))
            >> [ArgRepname(repname='者/しゃ', tid_list=1)]

        Args:
            case (str): 格の文字列
        
        Returns:
            list: 項の代表表記を格納したnamedtupleである ArgRepname のリスト
        """
        output = []
        for arg in self.arguments[case]:
            tid = arg.tid
            if self.tag_list[tid].head_prime_repname:
                rep = self.tag_list[tid].head_prime_repname 
            else:
                rep = self.tag_list[tid].repname
            output.append(ArgRepname(rep, tid)) 
        return output
    
    def get_orig_result(self):
        return self.tag_list[self.tid].features.get("格解析結果")

    def __parse_case_info_format(self, items, case_info_format):
        """ 格/述語項構造フォーマットを読み取る """
        if case_info_format == CaseInfoFormat.CASE:
            mycase = items[0]
            caseflag = items[1]
            midasi = items[2]
            tid = int(items[3])
            sdist = int(items[4])
            sid = items[5]
            eid = None
        elif case_info_format == CaseInfoFormat.PASv41:
            mycase = items[0]
            caseflag = items[1]
            midasi = items[2]
            eid = int(items[3])
            if eid in self.eid2tid:  # eidのエンティティが同一文内にない場合、KeyError
                tid = self.eid2tid[eid]
                sdist = self.tid2sdist[tid] if tid in self.tid2sdist else None
                sid = self.sid
            else:
                tid = -1  # FIXME: EIDが登録された文内のTag位置
                sdist = None
                sid = "-1"  # FIXME: EIDが登録された文のsid (複数文を辿れる必要がある)
        else:  # FIXME: tid,sidについてv4.1と同じ問題がある
            assert case_info_format == CaseInfoFormat.PASv42
            mycase = items[0]
            caseflag = items[1]
            midasi = items[2]
            sdist = int(items[3])
            tid = int(items[4])
            eid = int(items[5])
            sid = self.sid
        return mycase, caseflag, midasi, eid, tid, sdist, sid

    def __parse_case_analysis_items(self, analysis_result, case_info_format):
        """ 述語情報の設定・格情報の抽出 """
        assert isinstance(analysis_result, six.text_type)

        if analysis_result.count(":") < 2:  # For copula
            self.valid = False
            return

        if case_info_format == CaseInfoFormat.CASE:
            cf_pat = re.compile(r'(.+/.+):(.+):(.+?/[CNODEU]/.+?(?:/(?:-|\d+)){2}/[^;/]+)')
            arg_pat = re.compile(r';(.+?/[CNODEU]/.+?(?:/(?:-|\d+)){2}/[^;/]+)')
        elif case_info_format == CaseInfoFormat.PASv41:
            cf_pat = re.compile(r'(.+/.+):(.+):(.+?/[CNODEU]/.+?/(?:-|\d+))')
            arg_pat = re.compile(r';(.+?/[CNODEU]/.+?/(?:-|\d+))')
        else:
            assert case_info_format == CaseInfoFormat.PASv42
            cf_pat = re.compile(r'(.+/.+):(.+):(.+?/[CNODEU]/.+?(?:/(?:-?\d*)){3})')
            arg_pat = re.compile(r';(.+?/[CNODEU]/.+?(?:/(?:-?\d*)){3})')

        match = cf_pat.match(analysis_result)
        self.cfid = match.group(1) + ':' + match.group(2)
        cases = [match.group(3)]
        pos = match.end(3)
        while True:
            match = arg_pat.match(analysis_result, pos=pos)
            if match is None:
                break
            cases.append(match.group(1))
            pos = match.end(1)

        for k in cases:
            items = k.split('/')
            caseflag = items[1]
            if caseflag == 'U' or caseflag == '-':
                continue
            yield self.__parse_case_info_format(items, case_info_format)

    def __set_args(self, analysis_result, case_info_format):
        """ 述語項構造情報をself.argumentsに設定 """
        for items in self.__parse_case_analysis_items(analysis_result, case_info_format):
            (mycase, caseflag, midasi, eid, tid, sdist, sid) = items
            arg = Argument(sid=sid, tid=tid, eid=eid, midasi=midasi, flag=caseflag, sdist=sdist)
            self.arguments[mycase].append(arg)
