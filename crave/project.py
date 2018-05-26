import os
from crafter import CraftFactory

class Project(object):

    def __init__(self, name=None, db_opts = {}):
        # that's the dir were we will dump
        # the samples (and a copy of the vedis db)
        # until we support other backends

        self.name = name
        self.outdir = name

        if os.path.isdir(self.name):
            # an older project exists, we're adding up to it
            # open stuff like dbs! (:
            pass
        else:
            # setup a new crave project in the given dir
            os.mkdir(self.name)

        self.db = db_opts['backend'](self)

        self.crafter = CraftFactory(self)

    def add_sample(self, sample, tags):
        """ tags will define what kind of sample we are talking about,
        for example 'goodware', 'malware', or the set of mutations applied to it """
        pass

    def scan():
        pass

    def infer():
        pass
