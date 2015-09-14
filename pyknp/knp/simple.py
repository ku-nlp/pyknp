#-*- encoding: utf-8 -*-

from pyknp import KNP

my_knp = KNP()


def knp(input_str):
    return my_knp.parse(input_str)
