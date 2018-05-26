import logging
import os
import sys
import json
import argparse

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
    # craft all possibly interesting combinations of heuristics
    base_goodware = c.sample('base_samples/virut', Sample.MALWARE)
    base_malware = c.sample('base_samples/helloworld.exe', Sample.GOODWARE)

    # craft the samples

    for s in base_goodware.craft_heuristiscs():
        s.put()

    for s in base_malware.craft_heuristics():
        s.put()

    #scanner = Scanner(config.VT_API_KEY)
    c.scan()    # VirusTotal scan engine

    for r in c.infer():
        print "discovered %s" % r

    # first we store stuff in db and 
    # prepare the samples, we use the vedis db to
    # store stuff and query fast (? heopfully)

    #tester_manager = TesterManager(config)
    #tester_manager.inittests()

    ## set up a test ...
    #for s in crafted:

    #    scanner.submit()

def scan_it():
    pass

def infer_it():
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
    # scan_it()
    # infer_it()

if __name__ == '__main__':
    main()
