import logging
import os
import sys
import json
import argparse
from itertools import chain

from crave.utils import logs  # enable default logger
from crave.sample import TAGS


l = logging.getLogger('crave.crave')

from crave import Project, Crafter


""" tests currently "available"
  + goodware -> heuristics ~ +detections
  + malware -> heuristics ~ -detections
  + goodware -> packed ~ these are matching the packer!
  + malware -> packed -> break_oep ~ test static unpacking
  + goodware -> dropper (recognizable dropper?)
  + malware -> dropper (on demand scan == test emulation!)
"""

def load_samples(project, base_samples):

    samples_dir = base_samples.get('samples_path', 'base_samples')

    def gd(sample):
        return os.path.join(samples_dir, sample)

    def load_sample(entry, base_sample=None):

        sample = gd(entry['sample'])

        tags = entry['tags']
        if isinstance(tags, basestring):
            tags = [tags,]

        tags = [TAGS[t] for t in tags]
        if base_sample is None:
            tags.append(TAGS.base)

        heurs = entry.get('heur', [])
        s = project.sample(sample, tags, heurs, base_sample)
        s.put()

        for c in entry.get('childs', []):
            # load childs, keep ref of base sample
            load_sample(c, s)

    for s in base_samples.get('samples'):
        load_sample(s)


def pack_samples(project):
    pass


def gen_dropper():
    pass


def craft_it(project):

    # get interesting samples from DB and "mutate" them

    # first all heuristics for goodware/malware
    for s in project.db.get_tagged_samples([TAGS.base,]):
        for crafted in s.craft(tags=[TAGS.heuristics]):
            crafted.put()

    # second, corrupt OEP of packer to test static unpacking
    for s in project.db.get_tagged_samples([TAGS.packed,]):
        for crafted in s.craft(tags=[TAGS.teststaticpack], mutations=[Crafter.mutation_code_entryret,]):
            crafted.put()

    # we're done here, we test emulation with our dropper


def scan_it(project, submit):
    scanner = project.scanners['virustotal']
    if submit:
        scanner.scan_all()
    else:
        scanner.query_all()


def infer_it(project):
    project.decider.heuristics()


def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(prog=sys.argv[0])
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug log messages')

    parser.add_argument('projectname', type=str,
                        help='Name of the crave project (dir where to store results)')
    subparsers = parser.add_subparsers(
        help='Available crave commands', dest='subcommand')

    parser_load = subparsers.add_parser(
        'load', help='load samples from json config')
    parser_load.add_argument('base_samples', type=str,
                             help='base samples json file')

    parser_craft = subparsers.add_parser('craft', help='craft samples')

    parser_scan = subparsers.add_parser(
        'scan', help='Scan with virustotal the crafted samples')
    parser_scan.add_argument('--no-submit', action='store_true',
                             help='Do not submit samples, but retrieve results from VT')
    parser_scan.add_argument('--vt-key', type=str, help='VirusTotal API Key')

    parser_infer = subparsers.add_parser(
        'infer', help='Infer AV capabilities from scan results')


    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    if args.debug:
        logging.getLogger('crave').setLevel('DEBUG')

    with Project(args.projectname) as project:
        TAGS.add_tag('heuristics')  # define a new tag
        TAGS.add_tag('testemu')
        TAGS.add_tag('teststaticpack')
        # TODO: when everything is ported to the plugin architecture,
        # these will become part of the project class

        if args.subcommand == 'load':
            with open(args.base_samples) as f:
                base_samples = json.load(f)
            load_samples(project, base_samples)
        elif args.subcommand == 'craft':
            craft_it(project)
        elif args.subcommand == 'scan':
            project.scanners['virustotal'].set_key(args.vt_key)
            scan_it(project, not args.no_submit)
        elif args.subcommand == 'infer':
            infer_it(project)

if __name__ == '__main__':
    main()
