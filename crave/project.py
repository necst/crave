import os
import shutil
from .crafter import CraftFactory
from .sample import Sample, TAGS
from .cravedb.cravedb import DBFactory
from .plugin import PluginFactory
from .scanner import VirusTotal
from .decider import Decider
import logging


l = logging.getLogger('crave.project')


class Project(object):

    def __init__(self, name=None, db_opts={'backend': 'vedis'}, scanner_opts={}):
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

        self.scanners = {}
        pl = PluginFactory(VirusTotal, self, scanner_opts)

        self.decider = PluginFactory(Decider, self, {})

    def goodware(self, sample):
        return self.sample(sample, [TAGS.GOODWARE, ], [])

    def malware(self, sample):
        return self.sample(sample, [TAGS.MALWARE, ], [])

    def sample(self, sample, tags=[], mutations=[], base_sample=None):
        """ tags will define what kind of sample we are talking about,
        for example 'goodware', 'malware', or the set of mutations applied to it """
        return Sample(self, sample, tags, mutations, base_sample)

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
