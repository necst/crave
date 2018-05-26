import logging

from core import Tester
from core.findplugins import find_subclasses
from core.config import Configuration
from core import Crafter

logger = logging.getLogger('TesterManager')

class TesterManager:

    def __init__(self, config):
        self.config = config

    def inittests(self):
        logger.info('Loading Testers')
        available_testers = find_subclasses('core/testers', Tester)
        tests = self.config.tests
        self.testers = []

        # select Testers and set params
        if 'emu' in tests or 'all' in tests:
            t = [t for t in available_testers if 'emu' in t.__module__][0]
            self.testers.append((t, self.config))

        if 'static_unp' in tests or 'all' in tests:
            packers = self.config.samples.malware.packed
            for packer, packed in packers.iteritems():

                c = Configuration(test_config)
                c['packer'] = packer
                c['packed'] = packed
                t = [t for t in available_testers if 'heuristics_malware' in t.__module__][0]
                self.testers.append((t, c))

        if 'heuristics_malware' in tests or 'all' in tests:
            crafter = Crafter(self.config.samples.malware.sample)
            # crafted_samples = crafter.mutate()
            crafted_samples = []

            for crafted in crafted_samples:
                test_config = {}
                test_config['VT_API_KEY'] = self.config.VT_API_KEY
                test_config['original'] = self.config.samples.malware.sample
                test_config['mutated'] = crafted
                test_config['no_submit'] = self.config.no_submit

                c = Configuration(test_config)
                t = [t for t in available_testers if 'heuristics_malware' in t.__module__][0]
                self.testers.append((t, c))

        if 'heuristics_goodware' in tests or 'all' in tests:
            crafter = Crafter(self.config.samples.goodware.sample)
            # crafted_samples = crafter.mutate()
            crafted_samples = []

            for crafted in crafted_samples:
                test_config = {}
                test_config['mutated'] = crafted
                test_config['no_submit'] = self.config.no_submit

                c = Configuration(test_config)
                t = [t for t in available_testers if 'heuristics_goodware' in t.__module__][0]
                self.testers.append((t, c))

    def runtests(self):
        logger.info('Running Testers')

        for tester, param in self.testers:
            logger.info('Running Tester ({}) with param ({})'.format(tester,
                                                                     param))
            t = tester(param)
            t.run()
