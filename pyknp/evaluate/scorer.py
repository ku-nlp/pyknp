#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Scorer(object):

    def __init__(self, fp, fn, tp, tn):
        (self.fp, self.fn, self.tp, self.tn) = (fp, fn, tp, tn)
        self.count = None

    def __unicode__(self):
        dump = u"(fp, fn, tp, tn) = %s\n" % str((self.fp, self.fn, self.tp, self.tn))
        dump += u"Accuracy   : %.2f\n" % (self.accuracy() * 100)
        dump += u"Precision  : %.2f\n" % (self.precision() * 100)
        dump += u"Recall     : %.2f\n" % (self.recall() * 100)
        dump += u"F1         : %.2f\n" % (self.f_measure(1) * 100)
        return dump

    def accuracy(self):
        try:
            return float(self.tp + self.tn) / (self.fp + self.fn + self.tp + self.tn)
        except:
            return float('nan')

    def precision(self):
        try:
            return float(self.tp) / (self.tp + self.fp)
        except:
            return float('nan')

    def recall(self):
        try:
            return float(self.tp) / (self.tp + self.fn)
        except:
            return float('nan')

    def f_measure(self, beta=1.0):
        assert isinstance(beta, float)
        try:
            prec = self.precision()
            rec = self.recall()
            c = pow(beta, 2)
            return ((1 + c) * prec * rec) / (c * prec + rec)
        except:
            return float('nan')
