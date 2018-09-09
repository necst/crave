""" This module contains the classes related to the outcome of a scan """
from uuid import uuid4
import json

class Scan(Plugin):
    def __init__(self, sample, uuid=None, pending=False, done=False):
        self.pending = pending
        self.done = done
        self.sample = sample # sample triggering
        if uuid is not None:
            self._uuid = uuid # uuid for scan
        else:
            self._uuid = uuid4()
        self.scanner = scanner
        self.scan_results = []

    @property
    def uuid(self):
        return '{}_{}'.format(self.scanner, self.uuid)


class ScanResult(Plugin):
    """ this class represents a single scan for an AV, on a specific sample, at a given time, extra must be serializable..."""

    def __init__(self, sample, scan, uuid=None, av, label, version, update):
        if uuid:
            self.uuid = uuid
        else:
            self.uuid = UUID()

        self.scan = scan
        self.scanner = scan.scanner
        self.label = label
        self.sample = sample
        self.av = av  # we'll have a class also for this, we're building kind of a small orm-like system, but queries? cannot we model them in a better way?
        self.extra = extra

    def get(self):
        pass

    def put(self):
        pass
