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




    def get_scans(self, sample=[], sha256=[]):

        if sha256:
            h = sha256
        else:
            h = map(lambda s: s.sha256, sample)

        res = self._scans.mget(h)
        if res:
            return [json.loads(r) for r in res]
        return None

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

    def _pending(self, scanner):
        return self._db.Set('{}_pending'.format(scanner))

    @property
    def all_samples(self):
        # TODO: fix this
        for s in self._samples.keys():
            yield self.get_sample(s)

    def get_scans(scanner=None, av=None, uuids=[]):
        if scanner is not None:
            # get by scanner
            byscanner = ?

        if av is not None:
            byscanner = ?

        if len(uuids) > 0:
            scans = ?
    
        return byscanner & byav & uuids

    def get_pending_scans(scanner):
        # pending is a Set contaning scans UUIDS
        pending = self._pending(scanner)
        return self.get_scans(scanner, pending.to_set())

    def get_by_scanner(self, scanner):
        pass

    def get_by_av(self, av):
        pass

    @commit_on_success
    def put_scan_results(self, res):
        self._scanresults[res.uuid] = 

    @commit_on_success
    def put_scan(self, scan):

        scanner = scan.scanner

        if scan.pending:
            # add to pending Set
            self._pending(scanner).add(scan.uuid)
        else:
            self._pending(scanner).remove(scan.uuid)
            self._done(scanner).add(scan.uuid)

            self.put_scan_results(scan.scan_results)
            # we have just 

        # now we're going to be passed a scanner.Scan class
        # so we need to put the info for the scan itself,
        # but we also want to be able to query results for a specific sample
        # and for a specific AV, for each AV we want to be able
        # to get immediately all the results for a given sample

    def put_pending_scans(self, scans):
        for s in scans:
            self.put_scan(scan)

    def close(self):
        self._db.close()
