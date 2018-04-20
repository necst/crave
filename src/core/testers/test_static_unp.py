import os
import argparse

from time import sleep

from core import Tester
from submit import Submitter, Hash
from query import Scanner
from config import API_KEY
from utils import green
from labelizer import comparelabels


class TestStaticUnp(Tester):
    def __init__(self, key, payload, packed, no_submit=False):
        self.key = key
        self.payload = payload
        self.packed = packed
        self.no_submit = no_submit
        self.payload_report = None
        self.packed_report = None
        self.staticunp_results = {}

    def submit(self):
        if not self.no_submit:
            print '[+] Submitting malicious payload', self.payload
            payload_submitter = Submitter(self.key, self.payload)
            payload_submitter.run()

            print '[+] Submitting packed payload', self.packed
            packed_submitter = Submitter(self.key, self.packed)
            packed_submitter.run()

        hashes = []
        h = Hash(self.payload)
        h.calculate()
        hashes.append(h.sha256)
        h = Hash(self.packed)
        h.calculate()
        hashes.append(h.sha256)

        scanner = Scanner(self.key)
        scanner.list = hashes

        ready = False
        while not ready:
            if not self.no_submit:
                print '[+] Waiting for reports'
                sleep(60)
            ready = True
            print '[+] Getting reports'
            reports = scanner.scan()
            for entry in reports:
                if entry['response_code'] != 1:
                    ready = False

        print '[+] Got reports'
        self.payload_report = reports[0]
        self.packed_report = reports[1]

    def infer(self):
        print '[+] Selecting AVs'
        all_avs = set(self.payload_report['scans'].keys())

        payload_negatives = set()
        for av, outcome in self.payload_report['scans'].iteritems():
            if not outcome['detected']:
                payload_negatives.add(av)

        selected_avs = all_avs - payload_negatives
        selected_avs &= set(self.payload_report['scans'].keys())
        selected_avs &= set(self.packed_report['scans'].keys())

        print '[+] Inferring results'
        for av in selected_avs:
            payload_label = self.payload_report['scans'][av]['result']
            packed_label = self.packed_report['scans'][av]['result']

            if (payload_label and packed_label and
                comparelabels(payload_label, packed_label)):
                self.staticunp_results[av] = True
            else:
                self.staticunp_results[av] = False

    def printresults(self):
        print '\n[+] Static unpacking results:\n\n'
        print '# Selected AVs: {0}'.format(len(self.staticunp_results.keys()))
        print '------------------------------'
        do_emu = set()

        for av, emu_outcome in self.staticunp_results.iteritems():
            payload_label = self.payload_report['scans'][av]['result']
            packed_label = self.packed_report['scans'][av]['result']

            if emu_outcome:
                do_emu.add(av)
                print green('{: <22} static - {: <35}{: <35}'.format(
                    av,
                    payload_label,
                    packed_label))

            else:
                print'{: <22} ?????? - {: <35}{: <35}'.format(
                    av,
                    payload_label,
                    packed_label)


        print '# AVs that do static unpacking: {0}'.format(len(do_emu))

    def run(self):
        if not self.key:
            print '[!] ERROR: You didn\'t specify a valid VirusTotal API key.\n'
            return

        if not os.path.exists(self.payload):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.payload)
            return

        if not os.path.exists(self.packed):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.packed)
            return

        self.submit()
        self.infer()
        self.printresults()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('payload', type=str, help='Path to malicious payload')
    parser.add_argument('packed', type=str, help='Path to packed sample *with broken stub*')
    parser.add_argument('--no-submit', action='store_true', help='Do not submit samples. Only retrive reports')
    parser.add_argument('--key', type=str, action='store', default=API_KEY, help='VirusTotal API key')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    test = TestStaticUnp(
        args.key,
        args.payload,
        args.packed,
        args.no_submit)

    test.run()
