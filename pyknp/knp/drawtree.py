#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import re
from six.moves import range

POS_MARK = {
    u'特殊': '*',
    u'動詞': 'v',
    u'形容詞': 'j',
    u'判定詞': 'c',
    u'助動詞': 'x',
    u'名詞': 'n',
    u'固有名詞': 'N',
    u'人名': 'J',
    u'地名': 'C',
    u'組織名': 'A',
    u'指示詞': 'd',
    u'副詞': 'a',
    u'助詞': 'p',
    u'接続詞': 'c',
    u'連体詞': 'm',
    u'感動詞': '!',
    u'接頭辞': 'p',
    u'接尾辞': 's',
    u'未定義語': '?'
}


class DrawTree(object):

    def draw_tree(self, fh=None):
        """ 構文木を指定された fh に出力する．指定を省略した場合は，標準出力に出力される． """

        if fh:
            fh.write(self.sprint_tree())
        # 指定なしの場合は標準出力を用いる．
        else:
            print(self.sprint_tree(), end=' ')

    def sprint_tree(self):
        """ 構文木を文字列で返す． """
        leaves = self.draw_tree_leaves()
        limit = len(leaves)
        item = [[0 for j in range(limit)] for i in range(limit)]
        active_column = [0] * limit
        limit -= 1

        for i in range(limit):
            para_row = 1 if leaves[i].dpndtype == "P" else 0
            for j in range(i + 1, limit + 1):
                if j < leaves[i].parent_id:
                    if active_column[j] == 2:
                        item[i][j] = u"╋" if para_row else u"╂"
                    elif active_column[j] == 1:
                        item[i][j] = u"┿" if para_row else u"┼"
                    else:
                        item[i][j] = u"━" if para_row else u"─"
                elif j == leaves[i].parent_id:
                    if leaves[i].dpndtype == "P":
                        item[i][j] = u"Ｐ"
                    elif leaves[i].dpndtype == "I":
                        item[i][j] = u"Ｉ"
                    elif leaves[i].dpndtype == "A":
                        item[i][j] = u"Ａ"
                    else:
                        if active_column[j] == 2:
                            item[i][j] = u"┨"
                        elif active_column[j] == 1:
                            item[i][j] = u"┤"
                        else:
                            item[i][j] = u"┐"
                    if active_column[j] == 2:
                        # すでにＰからの太線があればそのまま
                        pass
                    elif para_row:
                        active_column[j] = 2
                    else:
                        active_column[j] = 1
                else:
                    if active_column[j] == 2:
                        item[i][j] = u"┃"
                    elif active_column[j] == 1:
                        item[i][j] = u"│"
                    else:
                        item[i][j] = u"　"

        line = [self.leaf_string(leaf) for leaf in self.draw_tree_leaves()]
        for i in range(limit):
            for j in range(i + 1, limit + 1):
                line[i] += item[i][j]

        max_length = max([self._str_real_length(l) for l in line])
        buf = ""
        for i in range(limit + 1):
            diff = max_length - self._str_real_length(line[i])
            buf += " " * diff
            buf += line[i] + leaves[i].pstring() + "\n"

        return buf

    def leaf_string(self, leaf):
        string = ""
        for mrph in leaf.mrph_list():
            string += mrph.midasi

            if re.search(u"^(?:固有名詞|人名|地名)$", mrph.bunrui):
                string += POS_MARK[mrph.bunrui]
            else:
                string += POS_MARK[mrph.hinsi]

        return string

    def _str_real_length(self, string):
        length = 0
        for char in string:
            if re.search("^[a-zA-Z\*\!\?]$", char):
                # 品詞情報は長さ1
                length += 1
            else:
                length += 2

        return length
