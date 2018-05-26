import logging
import os
import sys
import json
import argparse
from itertools import chain

from crave import Project
from crave.cravedb import VedisBackend

l = logging.getLogger('crave.crave')

# tests currently "available"
# goodware -> heuristics ~ +detections
# malware -> heuristics ~ -detections
# goodware -> packed ~ these are matching the packer!
# malware -> packed -> break_oep ~ test static unpacking
# goodware -> dropper (recognizable dropper?)
# malware -> dropper (on demand scan == test emulation!)


def craft_it(project, base_samples):

    c = project
    name = project.name

    # add base samples goodware/malware
    goodware = c.add_goodware(base_samples['goodware']['sample'])
    malware = c.add_malware(base_samples['malware']['sample'])

    # craft samples to test heuristics

    for s in chain(goodware.craft(), malware.craft()):
        s.put()

    # right now dropper generation is automated only
    # with mingw, we might want to use it at a later stage
    # (compilation options seems to able to change recognition too)
    # add base samples to test emu (dropper)

    # same for packers, for now let's load samples generated manually
    # we'll automate the packing process later
    # add base samples to test packers

def scan_it(project):
    pass

def infer_it(project):
    pass


def main():

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='PROG')
    parser.add_argument('name', type=str, help='Name of the crave project (dir where to store results)')
    subparsers = parser.add_subparsers(help='Available crave commands', dest='subcommand')

    # create the parser for the "a" command
    parser_a = subparsers.add_parser('craft', help='craft samples')
    parser_a.add_argument('base_samples', type=str, help='base samples json file')

    # create the parser for the "b" command
    parser_b = subparsers.add_parser('scan', help='Scan with virustotal the crafted samples')
    parser_b.add_argument('--vt-key', type=str, help='VirusTotal API Key')

    parser_b = subparsers.add_parser('infer', help='Infer AV capabilities from scan results')
    parser_b.add_argument('--baz', choices='XYZ', help='baz help')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    project = Project(args.name, {'backend': VedisBackend})

    if args.subcommand == 'craft':
        with open(args.base_samples) as f:
            base_samples = json.load(f)
        craft_it(project, base_samples)
    elif args.subcommand == 'scan':
        scan_it(project)
    elif args.subcommand == 'infer':
        infer_it(project)

if __name__ == '__main__':
    main()
