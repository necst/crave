import os
from vedis import Vedis


class VedisBackend():

    def __init__(self, project):
        self._project = project
        self.name = os.path.join(project.outdir, 'crave.db') if project.outdir is not None else ':mem:'

        self._db = Vedis(self.name)

    def get_sample(self, sample_hash):
        pass

    def put_sample(self, sample):

        sample.filename
        sample.hash
        sample.mutationchain

        pass

    def get_scan():
        pass

    def put_scan():
        pass
