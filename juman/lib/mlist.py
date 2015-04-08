class MList:
    def __init__(self, mrphs=[]):
        self.mrph = []
        for mrph in mrphs:
            self.push_mrph(mrph)
        self.MLIST_READONLY = False
    def mrph_list(self):
        return self.mrph
    def push_mrph(self, mrph):
        if self.MLIST_READONLY:
            return
        self.mrph.append(mrph)
    def set_readonly(self):
        self.MLIST_READONLY = True
    def set_mlist_readonly(self):
        self.set_readonly()
    def spec(self):
        spec = ""
        for mrph in self.mrph:
            spec = "%s%s" % (spec, mrph.spec())
            for doukei in mrph.doukei():
                spec = "%s@ %s" % (spec, doukei.spec())
        return spec
