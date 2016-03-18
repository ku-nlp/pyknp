#-*- encoding: utf-8 -*-

from __future__ import absolute_import
from pyknp import KNP

my_knp = KNP()


def knp(input_str):
    return my_knp.parse(input_str)
