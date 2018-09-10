""" This module contains the classes related to the outcome of a scan """
from uuid import uuid4
import json

class Scan(Plugin):
    def __init__(self, sample, uuid=None, pending=False):
        self.pending = pending
        self.sample = sample # sample triggering
        if uuid is not None:
            self._uuid = uuid # uuid for scan
        else:
            self._uuid = uuid4()
        self.scanner = scanner
        self.scan_results = []

    def put(self):
        return self.project.db.put_scan(self)

    def add_result(self, scan_result):
        self.scan_results.append(scan_result)
        self.project.db.put_scan_result(self, scan_result)

    @property
    def uuid(self):
        return '{}_{}'.format(self.scanner, self.uuid)


class ScanResult(Plugin):
    """ this class represents a single scan for an AV, on a specific sample, at a given time, extra must be serializable..."""

    def __init__(self, uuid=None, sample=None, scanner=None, scan_results=[]):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = uuid4()

        self.scan = scan
        self.scanner = scan.scanner
        self.label = label
        self.sample = sample
        self.av = av  # we'll have a class also for this, we're building kind of a small orm-like system, but queries? cannot we model them in a better way?
        self.extra = extra
