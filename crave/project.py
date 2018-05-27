import os
import shutil
from .crafter import CraftFactory
from .sample import Sample
from .cravedb.cravedb import DBFactory


class Project(object):

    def __init__(self, name=None, db_opts={}):
        # that's the dir were we will dump
        # the samples (and a copy of the vedis db)
        # until we support other backends

        self.name = name
        self.outdir = name
        # TODO:  use an in-memory db for quick tests
        self.crafter = CraftFactory(self)

        if not os.path.exists(name):
            os.mkdir(name)

        self.outdir = name

        self.db = DBFactory(self, db_opts)

        self.crafter = CraftFactory(self)

    def goodware(self, sample):
        return self.sample(sample, 'goodware')

    def malware(self, sample):
        return self.sample(sample, 'malware')

    def sample(self, sample, tags):
        """ tags will define what kind of sample we are talking about,
        for example 'goodware', 'malware', or the set of mutations applied to it """
        return Sample(self, sample)

    def scan():
        pass

    def infer():
        pass
