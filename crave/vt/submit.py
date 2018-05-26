#!/usr/bin/env python
import os
import sys
import json
import requests
import hashlib
import argparse

from core.vt.config import VT_SCAN_URL, VT_RESCAN_URL, HASHES_FILE


class Hash(object):
    def __init__(self, path):
        self.path = path
        self.md5 = ''
        self.sha256 = ''

    def get_chunks(self):
        fd = open(self.path, 'rb')
        while True:
            chunk = fd.read(16 * 1024)
            if not chunk:
                break

            yield chunk
        fd.close()

    def calculate(self):
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()

        for chunk in self.get_chunks():
            md5.update(chunk)
            sha256.update(chunk)

        self.md5 = md5.hexdigest()
        self.sha256 = sha256.hexdigest()

class Submitter(object):
    def __init__(self, key, path, rescan=False):
        self.key = key
        self.path = path
        self.rescan = rescan
        self.list = []

    def populate(self):
        paths = []

        if os.path.isfile(self.path):
            paths.append(self.path)
        else:
            for root, folders, files in os.walk(self.path):
                for file_name in files:
                    # Skip hidden files, might need an option for this.
                    if file_name.startswith('.'):
                        continue

                    file_path = os.path.join(root, file_name)
                    if os.path.exists(file_path):
                        paths.append(file_path)

        hashes_map = {}

        for path in paths:
            hashes = Hash(path)
            hashes.calculate()
            hashes_map[os.path.basename(path)] = hashes.sha256

            self.list.append({
                'path' : path,
                'md5' : hashes.md5,
                'sha256' : hashes.sha256
                })

        if os.path.isfile(HASHES_FILE):
            hashes_file = open(HASHES_FILE, 'r')
            old_map = json.loads(hashes_file.read())
            hashes_file.close()

            hashes_map.update(old_map)

        hashes_file = open(HASHES_FILE, 'w')
        hashes_file.write(json.dumps(hashes_map, indent=4))
        hashes_file.close()

    def submit(self):
        for entry in self.list:
            params = {'apikey': self.key}
            fname = os.path.basename(entry['path'])
            files = {'file': (fname, open(entry['path'], 'rb'))}

            # TODO check rescan

            try:
                response = requests.post(VT_SCAN_URL,
                    files=files,
                    params=params)
            except Exception as e:
                print '[!] ERROR: Cannot obtain results from VirusTotal: {0}\n'.format(e)

            response_json = response.json()

            if response_json['response_code'] == 0:
                print '[!] ERROR: Failed submission, {0}'.format(entry['path'])

    def run(self):
        if not self.key:
            print '[!] ERROR: You didn\'t specify a valid VirusTotal API key.\n'
            return

        if not os.path.exists(self.path):
            print '[!] ERROR: The target path {0} does not exist.\n'.format(self.path)
            return

        self.populate()
        self.submit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str, help='Path to the file or folder to submit on VirusTotal')
    parser.add_argument('--key', type=str, action='store', help='VirusTotal API key')
    parser.add_argument('--rescan', action='store_true', help='Force rescan')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    submit = Submitter(args.key, args.path, args.rescan)
    submit.run()
