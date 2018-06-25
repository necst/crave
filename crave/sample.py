import logging
import os
from crave.crafter.pe import PE
from hashlib import sha256

l = logging.getLogger('crave.sample')

class TAGS():
    MALWARE = 'malware',
    GOODWARE = 'goodware',
    HEUR = 'heur',
    PACK = 'pack',
    DROP = 'drop',
    UNKNOWN = 'unknown'


class Sample(object):

    def __init__(self, project, filename, tag=TAGS.UNKNOWN, mutations=[], base_sample=None):
        self.project = project
        self.file = filename
        self.filename = os.path.basename(filename)
        self.dir = os.path.dirname(filename)
        self.pe = PE(filename)
        self.sha256 = sha256(self.pe.write())
        self.tag = tag
        self.mutations = mutations
        self.base_sample = base_sample

    def put(self):
        self.project.db.put_sample(self)
        pass

    def get(self):
        #self.project.db.get_sample()
        pass

    def craft(self, mutations=None):
        """ apply all possible mutations to the sample and store
        in the database, we'll be ready to go and scan these,
        returns another instance of a Sample """
        if mutations is None:
            l.warning(
                    'empty list of mutations for %s, default to all heuristics',
                    self.filename)

            mutations = self.project.crafter.mutations

        for m in mutations:
            yield self.project.crafter(self, m)

    def to_json(self):
        d = {'file' : self.file,
            'tag' : self.tag,
            'mutations' : self.mutations}

        if self.base_sample is not None:
            d['base_sample'] = self.base_sample.sha256

        return d
