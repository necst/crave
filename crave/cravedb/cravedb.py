""" for now it implements a quick db backend with Vedis, potentially can be
expanded later to support other databases """
import os
import logging

#l = logging.getLogger('crave.cravedb')


class DBPlugin(object):

    def _init_db(self, project, db_opts):
        self.project = project
        self.db_opts = db_opts

    def __getattr__(self, name):
        print self.__dict__
        print name
        if name in self.__dict__:
            return self.__dict__[name]
        return None

    def connect(self):
        raise NotImplemented()



class DBFactory(object):

    def __new__(cls, *args, **kwargs):

        project = kwargs.get('project', None) or args[0]
        db_opts  = kwargs.get('db_opts', None) or args[1]

        backend = db_opts.get('backend') or 'vedis'

        if backend == 'vedis':
            binst = VedisBackend()

        binst._init_db(project, db_opts)
        print 'FAAAAAAAAAAAAAAAAAAAAAACK'
        binst.connect()

        return binst


    def __init__(self, project, db_opts):
        self.project = project
        self.name = os.path.join(project.outdir, 'crave.db') if project.outdir is not None else ':mem:'
        return super(DB, self).__init__()

    def get_sample(self, sample_hash):
        raise NotImplemented()

    def get_avresults(self, sample_hash):
        raise NotImplemented()

    def store_sample(self, sample):
        raise NotImplemented()

from .vedisbackend import VedisBackend
