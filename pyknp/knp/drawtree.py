# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import print_function
import re

POS_MARK = {
    '特殊': '*',
    '動詞': 'v',
    '形容詞': 'j',
    '判定詞': 'c',
    '助動詞': 'x',
    '名詞': 'n',
    '固有名詞': 'N',
    '人名': 'J',
    '地名': 'C',
    '組織名': 'A',
    '指示詞': 'd',
    '副詞': 'a',
    '助詞': 'p',
    '接続詞': 'c',
    '連体詞': 'm',
    '感動詞': '!',
    '接頭辞': 'p',
    '接尾辞': 's',
    '未定義語': '?'
}


def draw_tree(leaves, fh=None, show_pos=True):
    """ 構文木を指定された fh に出力する．指定を省略した場合は，標準出力に出力される． """

    if fh:
        fh.write(sprint_tree(leaves, show_pos=show_pos))
    # 指定なしの場合は標準出力を用いる．
    else:
        print(sprint_tree(leaves, show_pos=show_pos), end=' ')


def sprint_tree(leaves, show_pos=True):
    """ 構文木を文字列で返す． """
    limit = len(leaves)
    item = [[''] * limit for _ in range(limit)]
    active_column = [0] * limit
    limit -= 1

    for i in range(limit):
        para_row = 1 if leaves[i].dpndtype == "P" else 0
        for j in range(i + 1, limit + 1):
            if j < leaves[i].parent_id:
                if active_column[j] == 2:
                    item[i][j] = "╋" if para_row else "╂"
                elif active_column[j] == 1:
                    item[i][j] = "┿" if para_row else "┼"
                else:
                    item[i][j] = "━" if para_row else "─"
            elif j == leaves[i].parent_id:
                if leaves[i].dpndtype == "P":
                    item[i][j] = "Ｐ"
                elif leaves[i].dpndtype == "I":
                    item[i][j] = "Ｉ"
                elif leaves[i].dpndtype == "A":
                    item[i][j] = "Ａ"
                else:
                    if active_column[j] == 2:
                        item[i][j] = "┨"
                    elif active_column[j] == 1:
                        item[i][j] = "┤"
                    else:
                        item[i][j] = "┐"
                if active_column[j] == 2:
                    # すでにＰからの太線があればそのまま
                    pass
                elif para_row:
                    active_column[j] = 2
                else:
                    active_column[j] = 1
            else:
                if active_column[j] == 2:
                    item[i][j] = "┃"
                elif active_column[j] == 1:
                    item[i][j] = "│"
                else:
                    item[i][j] = "　"

    lines = [_leaf_string(leaf, show_pos) for leaf in leaves]
    for i in range(limit):
        for j in range(i + 1, limit + 1):
            lines[i] += item[i][j]

    max_length = max([_str_real_length(line) for line in lines])
    buf = ""
    for i in range(limit + 1):
        diff = max_length - _str_real_length(lines[i])
        buf += " " * diff
        buf += lines[i] + leaves[i].pstring() + "\n"

    return buf


def _leaf_string(leaf, show_pos):
    string = ""
    for mrph in leaf.mrph_list():
        string += mrph.midasi

        if show_pos:
            if re.search("^(?:固有名詞|人名|地名)$", mrph.bunrui):
                string += POS_MARK[mrph.bunrui]
            else:
                string += POS_MARK[mrph.hinsi]

    return string


def _str_real_length(string):
    length = 0
    for char in string:
        if re.search(r"^[a-zA-Z*!?]$", char):
            # 品詞情報は長さ1
            length += 1
        else:
            length += 2

    return length
