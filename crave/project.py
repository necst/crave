import os
from crafter import CraftFactory
from sample import Sample
import shutil

class Project(object):

    def __init__(self, name=None, db_opts = {}):
        # that's the dir were we will dump
        # the samples (and a copy of the vedis db)
        # until we support other backends

        self.name = name
        self.outdir = name
        self.crafter = CraftFactory(self)

        if os.path.exists(name):
            shutil.rmtree(name)
        os.mkdir(name)

        self.outdir = name

        self.db = db_opts['backend'](self)

        self.crafter = CraftFactory(self)

    def add_goodware(self, sample):
        return self.add_sample(sample, 'goodware')

    def add_malware(self, sample):
        return self.add_sample(sample, 'malware')

    def add_sample(self, sample, tags):
        """ tags will define what kind of sample we are talking about,
        for example 'goodware', 'malware', or the set of mutations applied to it """
        return Sample(self, sample)

    def scan():
        pass

    def infer():
        pass
