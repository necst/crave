import os
import argparse

from time import sleep

from core import Tester
from core.vt import Submitter, Hash
from core.vt import Scanner
from core.utils.colors import green


class TestHeuristicsGoodware(Tester):
    def __init__(self, key, original, mutated, no_submit=False):
        self.key = key
        self.original = original
        self.mutated = mutated
        self.no_submit = no_submit
        self.original_report = None
        self.mutated_report = None
        self.heuristics_results = {}

    def submit(self):
        if not self.no_submit:
            print '[+] Submitting original sample', self.original
            original_submitter = Submitter(self.key, self.original)
            original_submitter.run()

            print '[+] Submitting mutated sample', self.mutated
            mutated_submitter = Submitter(self.key, self.mutated)
            mutated_submitter.run()

        hashes = []
        h = Hash(self.original)
        h.calculate()
        hashes.append(h.sha256)
        h = Hash(self.mutated)
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
        self.original_report = reports[0]
        self.mutated_report = reports[1]

    def infer(self):
        print '[+] Selecting AVs'
        all_avs = set(self.mutated_report['scans'].keys())

        original_positives = set()
        for av, outcome in self.original_report['scans'].iteritems():
            if outcome['detected']:
                original_positives.add(av)

        selected_avs = all_avs - original_positives
        selected_avs &= set(self.original_report['scans'].keys())

        print '[+] Inferring results'
        for av in selected_avs:
            if self.mutated_report['scans'][av]['detected']:
                self.heuristics_results[av] = True
            else:
                self.heuristics_results[av] = False

    def printresults(self):
        print '\n[+] Static unpacking results:\n\n'
        print '# Selected AVs: {0}'.format(len(self.heuristics_results.keys()))
        print '------------------------------'
        do_emu = set()

        for av, emu_outcome in self.heuristics_results.iteritems():
            original_label = self.original_report['scans'][av]['result']
            mutated_label = self.mutated_report['scans'][av]['result']

            if emu_outcome:
                do_emu.add(av)
                print green('{: <22} Heuristic - {: <35}{: <35}'.format(
                    av,
                    original_label,
                    mutated_label))

            else:
                print'{: <22} Nope      - {: <35}{: <35}'.format(
                    av,
                    original_label,
                    mutated_label)


        print '# New detections: {0}'.format(len(do_emu))

    def run(self):
        if not self.key:
            print '[!] ERROR: You didn\'t specify a valid VirusTotal API key.\n'
            return

        if not os.path.exists(self.original):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.original)
            return

        if not os.path.exists(self.mutated):
            print '[!] ERROR: File {0} does not exist.\n'.format(self.mutated)
            return

        self.submit()
        self.infer()
        self.printresults()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('original', type=str, help='Path to original sample')
    parser.add_argument('mutated', type=str, help='Path to mutated sample')
    parser.add_argument('--no-submit', action='store_true', help='Do not submit samples. Only retrive reports')
    parser.add_argument('--key', type=str, action='store', help='VirusTotal API key')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    test = TestHeuristicsGoodware(
        args.key,
        args.original,
        args.mutated,
        args.no_submit)

    test.run()
