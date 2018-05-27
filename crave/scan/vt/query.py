#!/usr/bin/env python
import os
import sys
import json
import requests
import hashlib
import argparse

from core.vt.config import VT_RES_URL, HASHES_FILE, DATA_FOLDER


class Scanner(object):
    def __init__(self, key, file=HASHES_FILE):
        self.key = key
        self.file = file
        self.list = []

    def populate(self):
        self.list = json.loads(open(self.file).read()).values()

    def scan(self):
        params = {'apikey': self.key, 'resource': ','.join(self.list)}

        try:
            response = requests.get(VT_RES_URL, params=params)
            report = response.json()
        except Exception as e:
            print '[!] ERROR: Cannot obtain results from VirusTotal: {0}\n'.format(e)
            return

        results = []
        if type(report) is dict:
            results.append(report)
        elif type(report) is list:
            results = report

        for entry in results:
            sha256 = entry['resource']

            if entry['response_code'] == 0:
                print 'WARNING: {0} NOT FOUND'.format(sha256)

            else:
                # TODO check if file exists?
                dump_file = open(os.path.join(DATA_FOLDER, sha256), 'w')
                dump_file.write(json.dumps(entry, indent=4))
                dump_file.close()

        return results

    def run(self):
        if not self.key:
            print '[!] ERROR: You didn\'t specify a valid VirusTotal API key.\n'
            return

        if not os.path.exists(self.file):
            print '[!] ERROR: The hashes file {0} does not exist.\n'.format(self.file)
            return

        self.populate()
        return self.scan()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, default=HASHES_FILE, help='Path to the hashes file')
    parser.add_argument('--key', type=str, action='store', help='VirusTotal API key')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    scan = Scanner(args.key, args.file)
    scan.run()
