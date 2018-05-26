import os
import argparse

from time import sleep

from core import Tester
from core.vt import Submitter, Hash
from core.vt import Scanner
from core.utils.colors import green
from core.labelizer import comparelabels


class Emulation(Tester):
    # def __init__(self, key, gooddropper, payload, maldropper, no_submit=False):
    def __init__(self, config):
        self.key = config.VT_API_KEY
        self.gooddropper = config.samples.goodware.dropper
        self.payload = config.samples.malware.sample
        self.maldropper = config.samples.malware.dropper
        self.no_submit = config.no_submit

        self.gooddropper_report = None
        self.payload_report = None
        self.maldropper_report = None
        self.emulation_results = {}

    def submit(self):
        if not self.no_submit:
            print '[+] Submitting goodware dropper', self.gooddropper
            gooddropper_submitter = Submitter(self.key, self.gooddropper)
            gooddropper_submitter.run()

            print '[+] Submitting malicious payload', self.payload
            payload_submitter = Submitter(self.key, self.payload)
            payload_submitter.run()

            print '[+] Submitting malware dropper', self.maldropper
            maldropper_submitter = Submitter(self.key, self.maldropper)
            maldropper_submitter.run()

        hashes = []
        h = Hash(self.gooddropper)
        h.calculate()
        hashes.append(h.sha256)
        h = Hash(self.payload)
        h.calculate()
        hashes.append(h.sha256)
        h = Hash(self.maldropper)
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
        self.gooddropper_report = reports[0]
        self.payload_report = reports[1]
        self.maldropper_report = reports[2]

    def infer(self):
        print '[+] Selecting AVs'
        all_avs = set(self.payload_report['scans'].keys())

        gooddropper_positives = set()
        for av, outcome in self.gooddropper_report['scans'].iteritems():
            if outcome['detected']:
                gooddropper_positives.add(av)

        payload_negatives = set()
        for av, outcome in self.payload_report['scans'].iteritems():
            if not outcome['detected']:
                payload_negatives.add(av)

        selected_avs = all_avs - gooddropper_positives - payload_negatives
        selected_avs &= set(self.payload_report['scans'].keys())
        selected_avs &= set(self.maldropper_report['scans'].keys())

        print '[+] Inferring results'
        for av in selected_avs:
            payload_label = self.payload_report['scans'][av]['result']
            maldropper_label = self.maldropper_report['scans'][av]['result']

            if (payload_label and maldropper_label
                and comparelabels(payload_label, maldropper_label)):
                self.emulation_results[av] = True
            else:
                self.emulation_results[av] = False

    def printresults(self):
        print '\n[+] Emulation results:\n\n'
        print '# Selected AVs: {0}'.format(len(self.emulation_results.keys()))
        print '------------------------------'
        do_emu = set()

        for av, emu_outcome in self.emulation_results.iteritems():
            payload_label = self.payload_report['scans'][av]['result']
            maldropper_label = self.maldropper_report['scans'][av]['result']
            # good_label = self.gooddropper_report['scans'][av]['result']

            if emu_outcome:
                do_emu.add(av)
                print green('{: <22}{} - {: <35}{: <35}'.format(
                    av,
                    emu_outcome,
                    payload_label,
                    maldropper_label))

            else:
                print'{: <22}{} - {: <35}{: <35}'.format(
                    av,
                    emu_outcome,
                    payload_label,
                    maldropper_label)


        print '# AVs that do emulation: {0}'.format(len(do_emu))

    def run(self):
        if not self.key:
            print '[!] ERROR: You didn\'t specify a valid VirusTotal API key.\n'
            return

        if not os.path.exists(self.gooddropper):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.gooddropper)
            return

        if not os.path.exists(self.payload):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.payload)
            return

        if not os.path.exists(self.maldropper):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.maldropper)
            return

        self.submit()
        self.infer()
        self.printresults()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('gooddropper', type=str, help='Path to goodware dropper')
    parser.add_argument('payload', type=str, help='Path to malicious payload')
    parser.add_argument('maldropper', type=str, help='Path to malware dropper')
    parser.add_argument('--no-submit', action='store_true', help='Do not submit samples. Only retrive reports')
    parser.add_argument('--key', type=str, action='store', help='VirusTotal API key')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    test = TestEmu(
        args.key,
        args.gooddropper,
        args.payload,
        args.maldropper,
        args.no_submit)

    test.run()
