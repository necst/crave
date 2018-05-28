from .cravedb import DBPlugin
from vedis import Vedis
import logging
import os
import json

l = logging.getLogger('crave.cravedb.vedisbackend')
DB_NAME = 'crave.db'

class VedisBackend(DBPlugin):

    def connect(self):
        path = os.path.join(self.project.outdir, DB_NAME)
        self._db = Vedis(path)
        self._db['init'] = True

    def get_sample(self, sample):
        db = self._db

        db[sample.sha256] = sample

    def put_sample(self, sample):

        h = self._db.Hash('samples')

        h[sample.sha256] = json.dumps({
            'filename': sample.filename,
            'mutations': []})


    def get_scan():
        pass

    def put_scan():
        pass
