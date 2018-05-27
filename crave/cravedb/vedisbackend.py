from .cravedb import DBPlugin
from vedis import Vedis
import logging
import os

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

        sample.filename
        sample.hash
        sample.mutationchain

        pass

    def get_scan():
        pass

    def put_scan():
        pass
