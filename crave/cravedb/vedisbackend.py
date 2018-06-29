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
        return Sample(
                self.project, j['file'], j['tags'],
                j['mutations'], j.get('base_sample', None))

    def put_sample(self, sample):
        self._samples[sample.sha256] = sample.to_json()

        # keep reference of the sample for each tag :)
        for t in sample.tags:
            self.put_tag(t, sample.sha256)

        self._db.commit()

    def put_scan(self, scan, sample=None, sha256=None):
        if sha256:
            h = sha256
        else:
            h = sample.sha256
        self._scans[h] = json.dumps(scan)
        self._db.commit()

    def get_scan(self, sample=None, sha256=None):
        if sha256:
            h = sha256
        else:
            h = sample.sha256
        res = self._scans[h]
        if res:
            return json.loads(res)
        return None

    def put_tag(self, tag, sha256):
        t = self._db.Set('tag_' + tag)
        t.add(sha256)

    def get_tagged_samples(self, tag):
        return self._db.Set('tag_' + tag)

    @property
    def _samples(self):
        return self._db.Hash('samples')

    @property
    def _scans(self):
        return self._db.Hash('scans')

    @property
    def all_samples(self):
        # no way to use a generator with vedis
        # still ok for small analyses, we'll need to
        # support other DBs to reduce memory usage
        for s in self._samples.keys():
            yield self.get_sample(s)
