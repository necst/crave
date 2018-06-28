from .cravedb import DBPlugin
from vedis import Vedis
import logging
import os
import json
from ..sample import Sample


l = logging.getLogger('crave.cravedb.vedisbackend')
DB_NAME = 'crave.db'

class VedisBackend(DBPlugin):

    def connect(self):
        path = os.path.join(self.project.outdir, DB_NAME)
        self._db = Vedis(path)

    def get_sample(self, sha256):
        s = self._samples[sha256]
        j = json.loads(s)
        l.debug(j)
        return Sample(self.project, j['file'], j['tags'], j['mutations'], j.get('base_sample', None))

    def put_sample(self, sample):
        self._samples[sample.sha256] = sample.to_json()

        # keep reference of the sample for each tag :)
        self._tags[sample.tags] = sample.sha256

        self._db.commit()

    @property
    def _samples(self):
        return self._db.Hash('samples')

    @property
    def _tags(self):
        return self._db.Hash('tags')

    @property
    def all_samples(self):
        # no way to use a generator with vedis
        # still ok for small analyses, we'll need to
        # support other DBs to reduce memory usage
        for s in self._samples.keys():
            yield self.get_sample(s)
