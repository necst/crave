from ..plugin import Plugin
from collections import defaultdict
from ..sample import TAGS
from ..utils.colors import *
import logging

l = logging.getLogger('crave.decider')


class Decider(Plugin):

    def heuristics(self, tag):

        avs = defaultdict(dict)

        #.scanner = self.project.scanners['virustotal']
        for s in self.project.db.get_tagged_samples(tag):
            # we have sha256 of the sample here
            #sample = self.project.db.get_sample(s)
            scan = self.project.db.get_scan(sample)
            scans = scan['scans']

            # false positive = detected but goodware
            # false negative = not detected but malware

            for av in scans:
                avs[av]['_'.join(sample.mutations)] = {
                    'false_positive': 0,
                    'false_negative': 0}

            # we need a method that keeps track of tp/tn/fp/fn by giving it
            # a lambda function that has sample,scans as inputs, should suffice
            # for all of our current tests
            for av in scans:
                if TAGS.GOODWARE in sample.tags and scans[av]['detected']:
                    avs[av]['_'.join(sample.mutations)]['false_positive'] += 1
                if TAGS.MALWARE in sample.tags and not scans[av]['detected']:
                    avs[av]['_'.join(sample.mutations)]['false_negative'] += 1

            for av in avs:
                l.info(blue('Heuristics results for %s' % av))
                for m in avs[av]:
                    fp = avs[av][m]['false_positive']
                    fn = avs[av][m]['false_negative']
                    text = ('%20s:\tFP: %d\tFN: %d' % (
                        m, fp, fn))
                    if fp or fn:
                        text = red(text)
                    l.info(text)

    def static_unpacking(self, ):
        for s in project.db.get_tagged_samples([TAGS.teststaticpack,]):
            pass

        sample = malware.get_sample()  # (?) o gli passiamo un sample direttamente
        packed = sample.get_packed()
        broke_oep = packed.get_heur('retoep')

        # and here infer if it does static unpacking
        return {}

    def emulation(self, goodware, malware):
        # we need to query
        # goodware -> dropper
        # malware -> dropper
        # if it recognize the malicious dropper
        # as original sample variant, we have a
        # av that is able to emulate the shit
        goodware = self.project.get_sample(goodware)
        malware = self.project.get_sample(malware)

        gw_dropper = goodware.get_dropper()
        mw_dropper = malware.get_dropper()

        # look at scan results and infer
        return {}
