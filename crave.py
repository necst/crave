import logging
import os
import sys
import json
import argparse
from itertools import chain

from crave.utils import logs  # enable default logger
from crave.sample import TAGS


l = logging.getLogger('crave.crave')

from crave import Project

try:
    from vt import vtkey
except:
    vtkey = None

""" tests currently "available"
  + goodware -> heuristics ~ +detections
  + malware -> heuristics ~ -detections
  + goodware -> packed ~ these are matching the packer!
  + malware -> packed -> break_oep ~ test static unpacking
  + goodware -> dropper (recognizable dropper?)
  + malware -> dropper (on demand scan == test emulation!)
"""

def load_samples(project, base_samples):
    p = project
    name = project.name

    samples_dir = base_samples.get('samples_dir', 'base_samples')

    def gd(sample):
        return os.path.join(samples_dir, sample)

    # add base samples goodware/malware
    goodware = p.goodware(gd(base_samples['goodware']['sample']))
    malware = p.malware(gd(base_samples['malware']['sample']))
    goodware.put()
    malware.put()   # put in database

def pack_samples(project):
    pass

def gen_dropper():
    pass

def craft_it(project, base_samples):

    p = project
    name = project.name

    for s in chain(goodware.craft([TAGS.HEUR, ]), malware.craft([TAGS.HEUR, ])):
        s.put()

def scan_it(project, no_submit):
    if not no_submit:
        project.scanner.scan_all()
    project.scanner.query_all()


def infer_it(project):
    project.decider.heuristics()


def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('--vt-key', type=str, help='VirusTotal API Key')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug log messages')

    parser.add_argument('name', type=str,
                        help='Name of the crave project (dir where to store results)')
    subparsers = parser.add_subparsers(
        help='Available crave commands', dest='subcommand')

    parser_load = subparsers.add_parser('load', help='load samples from json config')
    parser_load.add_argument('base_samples', type=str, help='base samples json file')

    parser_craft = subparsers.add_parser('craft', help='craft samples')

    parser_scan = subparsers.add_parser(
            'scan', help='Scan with virustotal the crafted samples')
    parser_scan.add_argument('--no-submit', action='store_true',
            help='Do not submit samples, but retrieve results from VT')

    parser_infer = subparsers.add_parser(
        'infer', help='Infer AV capabilities from scan results')
    # parser_c.add_argument('--baz', choices='XYZ', help='baz help')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    if args.debug:
        logging.getLogger('crave').setLevel('DEBUG')

    project = Project(args.name, vtkey or args.vt_key)

    if args.subcommand == 'load':
        with open(args.base_samples) as f:
            base_samples = json.load(f)
        load_samples(project, base_samples)
    elif args.subcommand == 'craft':
        craft_it(project, base_samples)
    elif args.subcommand == 'scan':
        scan_it(project, args.no_submit)
    elif args.subcommand == 'infer':
        infer_it(project)


if __name__ == '__main__':
    main()
