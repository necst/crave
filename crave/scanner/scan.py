""" This module contains the classes related to the outcome of a scan """
from ..plugin import Plugin
from uuid import uuid4
import json

class Scan():
    def __init__(self, sample, scanner, uuid=None, pending=False, scan_id=None, scan_results=[]):
        self.pending = pending
        self.sample = sample
        self.uuid = uuid if uuid is not None else uuid4() # uuid for scan
        self.scanner = scanner
        self.scan_results = scan_results
        self.scan_id = scan_id  # unique id to retrieve from scanner

    def put(self):
        return self.project.db.put_scan(self)

    def add_result(self, scan_result):
        self.scan_results.append(scan_result)
        self.project.db.put_scan_result(self, scan_result)

    def __str__(self):
        return str(self.uuid)

    def to_dict(scan):
        return {'pending': scan.pending,
                'sample': scan.sample.sha256,
                'scanner': scan.scanner,
                'scan_id': scan.scan_id,
                'uuid': scan.uuid,
                'scan_results': [s.uuid for s in scan.scan_results]}

class ScanResult():
    """ this class represents a single scan for an AV, on a specific sample, at a given time, extra must be serializable..."""

    def __init__(self, sample, scanner, scan, av, label, update, version, uuid=None):
        self.uuid = uuid if uuid else uuid4()
        self.scan = scan
        self.scanner = scanner
        self.label = label
        self.sample = sample
        self.av = av
