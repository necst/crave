import os
import shutil
from .crafter import CraftFactory
from .sample import Sample, TAGS
from .cravedb.cravedb import DBFactory
from .plugin import PluginFactory
from .scanner import Scanner
import logging

l = logging.getLogger('crave.project')

class Project(object):

    def __init__(self, name=None, vt_key=None, db_opts={'backend': 'vedis'}, scanner_opts={}):
        # that's the dir were we will dump
        # the samples (and a copy of the vedis db)
        # until we support other backends

        self.name = name
        self.outdir = name
        self._vt_key = vt_key
        # TODO:  use an in-memory db for quick tests
        self.crafter = CraftFactory(self)

        if not os.path.exists(name):
            os.mkdir(name)

        self.outdir = name
        self.db = DBFactory(self, db_opts)
        self.crafter = CraftFactory(self)

        self.scanner = PluginFactory(Scanner, self, scanner_opts)

    def goodware(self, sample):
        return self.sample(sample, [TAGS.GOODWARE,], [])

    def malware(self, sample):
        return self.sample(sample, [TAGS.MALWARE,], [])

    def sample(self, sample, tags, mutations):
        """ tags will define what kind of sample we are talking about,
        for example 'goodware', 'malware', or the set of mutations applied to it """
        return Sample(self, sample, tags=tags, mutations=mutations)

    def scan():
        pass

    def infer():
        pass
