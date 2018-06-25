""" for now it implements a quick db backend with Vedis, potentially can be
expanded later to support other databases """
import os
import logging

l = logging.getLogger('crave.cravedb')


class DBPlugin(object):

    def _init_db(self, project, db_opts):
        self.project = project
        self.db_opts = db_opts

    def connect(self):
        raise NotImplementedError()

    def get_sample(self, sample_hash):
        raise NotImplementedError()

    def get_avresults(self, sample_hash):
        raise NotImplementedError()

    def put_sample(self, sample):
        raise NotImplementedError()

    @property
    def all_samples(self):
        raise NotImplementedError()


class DBFactory(object):

    def __new__(cls, *args, **kwargs):

        project = kwargs.get('project', None) or args[0]
        db_opts  = kwargs.get('db_opts', None) or args[1]

        backend = db_opts.get('backend') or 'vedis'

        if backend == 'vedis':
            binst = VedisBackend()

        binst._init_db(project, db_opts)
        binst.connect()

        return binst

from .vedisbackend import VedisBackend
