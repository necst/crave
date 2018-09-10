from .cravedb import DBPlugin
from vedis import Vedis
import logging
import os
import json
from ..sample import Sample
from functools import wraps

l = logging.getLogger('crave.cravedb.vedisbackend')
DB_NAME = 'crave.db'

def commit_on_success(f):
    @wraps(f)
    def wrapper(self, *args, **kwds):
        try:
            with self._db.transaction():
                r = f(self, *args, **kwds)
        except:
            l.exeception("%s, raised an exception, rolling back", f)
            self._db.rollback()
            raise
        else:
            self._db.commit()

        return r
    return wrapper


class VedisBackend(DBPlugin):

    def connect(self):
        path = os.path.join(self.project.outdir, DB_NAME)
        self._db = Vedis(path)

    def get_sample(self, sha256):
        s = self._samples[sha256]
        j = json.loads(s)
        bs = j.get('base_sample', None)
        if bs is not None:
            bs = self.get_sample(bs)
            #watch out for recursion!

        return Sample(
                self.project, j['file'], j['tags'],
                j['mutations'], bs)

    @commit_on_success
    def put_sample(self, sample):
        self._samples[sample.sha256] = sample.to_json()

        # keep reference of the sample for each tag :)
        for t in sample.tags:
            self.put_tag(t, sample.sha256)

    @commit_on_success
    def put_tag(self, tag, sha256):
        t = self._db.Set('tag_' + tag)
        t.add(sha256)

    def get_tagged_samples(self, tag):
        if isinstance(tag, basestring):
            tag = [tag,]
        for t in tag:
            for s in self._db.Set('tag_' + t):
                yield self.get_sample(s)

    @property
    def _samples(self):
        return self._db.Hash('samples')

    @property
    def _scans(self):
        return self._db.Hash('scans')

    def _pending_scans(self, scanner):
        return self._db.Set('{}_pending'.format(scanner))

    def get_pending_scans(self, scanner):
        return [Scan(uuid=p) for p in self._pending_scans(scanner)]

    @property
    def all_samples(self):
        # TODO: fix this
        for s in self._samples.keys():
            yield self.get_sample(s)

    """def get_scans(scanner=None, av=None, uuids=[]):
        if scanner is not None:
            # get by scanner
            byscanner = ?

        if av is not None:
            byav = ?

        if len(uuids) > 0:
            scans = ?

        return byscanner & byav & uuids"""

    @commit_on_success
    def _put_scan_results(self, scan_result):
        self._scanresults[res.uuid] = scan_result
        # "update" the set of scanresults for a given scan

    def scan_to_dict(self):
        return {
                'label': self.label,
                'sample': sample.sha256,
                'av': av,
                'extra': extra }

    """def scan_from_dict(cls, d):
        return cls(d['uuid'], ...)"""

    @commit_on_success
    def put_scan(self, scan):

        scanner = scan.scanner.short_name

        if scan.pending:
            # add to pending Set
            self._pending(scanner).add(scan.uuid)
        else:
            self._pending(scanner).remove(scan.uuid)
            self._done(scanner).add(scan.uuid)

            self._put_scan_results(scan.scan_results)

        self._scans[scan.uuid] = json.dumps(scan_to_dict(scan))

        l.debug("Scan %s stored in database", scan)

    def get_scan_results(self, av):
        pass

    def close(self):
        self._db.close()
