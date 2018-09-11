from .cravedb import DBPlugin
from vedis import Vedis
import logging
import os
import json
from ..sample import Sample
from ..scanner import Scan
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
            l.exception("%s, raised an exception, rolling back", f)
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

    def _done_scans(self, scanner):
        return self._db.Set('{}_done'.format(scanner))

    def get_pending_scans(self, scanner):
        pending = self._pending_scans(scanner)

        if len(pending) == 0:
            return []

        scans = []

        for p in pending:
            d = self._get_scan(p)
            scans.append(Scan(
                scanner=scanner, uuid=d['uuid'], 
                sample=d['sample'], scan_id=d['scan_id'],
                scan_results=d['scan_results']))
        return scans

    @property
    def all_samples(self):
        # TODO: fix this
        for s in self._samples.keys():
            yield self.get_sample(s)

    @commit_on_success
    def _put_scan_results(self, scan_result):
        self._scanresults[res.uuid] = scan_result
        # "update" the set of scanresults for a given scan

    @staticmethod
    def res_to_dict(scan):
        return {
                'label': scan.label,
                'sample': scan.sample.sha256,
                'av': scan.av,
                'extra': scan.extra }

    def _get_scan(self, uuid):
        return self._db.Hash(uuid)

    def _get_scan_result(self, scan):
        return self._db.Set(scan.uuid + '_results')

    def _res_by_sample(self, sample):
        return self._db.Set(scan.sample.sha + '_results')

    def _res_by_av(self, av):
        return self._db.Set(av + '_results')

    def _scan_by_sample(self, sample):
        return self._db.Set(sample.sha256 + '_scans')

    @commit_on_success
    def put_scan(self, scan):

        scanner = scan.scanner.short_name

        if scan.pending:
            # add to pending Set
            self._pending_scans(scanner).add(scan.uuid)

        else:
            self._pending_scans(scanner).remove(scan.uuid)

            self._put_scan_results(scan.scan_results)
            self._done_scan(scanner).add(scan.uuid)

            self._scan_by_sample(scan.sample).add(scan.uuid)

            for res in scan.scan_results:
                self._results(res.uuid).update(**res.to_dict())
                # add its reference to sets for quick querying
                self._res_by_sample(scan.sample).add(res.uuid)
                self._res_by_av(res.av).add(res.uuid)

        self._get_scan(scan.uuid).update(**scan.to_dict())

        l.debug("Scan %s stored in database", scan)

    def get_scan_results(self, av):
        pass

    def close(self):
        self._db.close()
