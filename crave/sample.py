import logging
import os
from crave.crafter.pe import PE
from hashlib import sha256

l = logging.getLogger('crave.sample')

class TAGS():
    MALWARE = 'malware'
    GOODWARE = 'goodware'
    HEUR = 'heur'
    PACK = 'pack'
    DROP = 'drop'
    UNKNOWN = 'unknown'


# TODO make this a crave plugin
class Sample(object):

    def __init__(self, project, filename, tags=[TAGS.UNKNOWN,], mutations=[], base_sample=None):
        self.project = project
        self.file = filename
        self.filename = os.path.basename(filename)
        self.dir = os.path.dirname(filename)
        self.pe = PE(filename)
        self.sha256 = sha256(self.pe.write()).hexdigest()
        self.tags = tags

        self.mutations = mutations
        self.base_sample = base_sample

    def put(self):
        l.debug('Adding sample %s to database > %s, %s',
                self.sha256, self.tags, self.mutations)
        self.project.db.put_sample(self)

    def craft(self, tags=[], mutations=[]):
        """ apply all possible mutations to the sample and store
        in the database, we'll be ready to go and scan these,
        returns another instance of a Sample """
        if not mutations:
            l.warning(
                    'Empty list of mutations for %s (%s), default to all heuristics',
                    self.filename, self.sha256)

            mutations = self.project.crafter.mutations

        for m in mutations:
            yield self.project.crafter(self, m, tags)

    def to_json(self):
        import json
        d = {'file' : self.file,
            'tags' : self.tags,
            'mutations' : self.mutations}

        if self.base_sample is not None:
            d['base_sample'] = self.base_sample.sha256

        return json.dumps(d)
