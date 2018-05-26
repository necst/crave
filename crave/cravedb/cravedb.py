""" for now it implements a quick db backend with Vedis, potentially can be
expanded later to support other databases """
from vedis import Vedis

class CraveDB(object):

    def __init__(self, dbname):
        self._db = Vedis(dbname)
        super(CraveDB, self).__init__()

    def get_sample(sample_hash):
        pass

    def get_avresults(sample_hash):
        pass

    def store_sample():
        """ ? """
        pass
