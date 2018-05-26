import logging
import os
from crave.crafter.pe import PE

l = logging.getLogger('crave.sample')

class Sample(object):

    def __init__(self, project, filename):
        self.project = project
        self.file = filename
        self.filename = os.path.basename(filename)
        self.dir = os.path.dirname(filename)
        self.pe = PE(filename)

    def put(self):
        self.project.db.put_sample()

    def get(self):
        self.project.db.get_sample()

    def craft(self, mutations=None):
        """ apply all possible mutations to the sample and store
        in the database, we'll be ready to go and scan these,
        returns another instance of a Sample """
        if mutations is None:
            l.warning('empty list of mutations for %s, default to all heuristics', self.filename)
            mutations = self.project.crafter.mutations

        for m in mutations:
            self.project.crafter(self, m)
