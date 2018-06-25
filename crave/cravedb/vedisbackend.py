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

    def get_sample(self, sample):
        db = self._db

        db[sample.sha256] = sample

    def put_sample(self, sample):

        db = self._db

        samples = db.Hash('samples')
        samples[sample.sha256] = sample.to_json()

        tags = db.Hash('tags')
        samples[sample.tag] = sample.sha256

    def get_scan():
        pass

    def put_scan():
        pass
