import os
import sys
import json
import argparse

from core.config import Configuration
from core import Crafter
from core import Decider


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help='Path to config file')
    parser.add_argument('output_folder', type=str, help='Path to output folder')

    try:
        args = parser.parse_args()
    except IOError as e:
        parser.error(e)
        sys.exit()

    config = Configuration.loadConf(args.config_file)


if __name__ == '__main__':
    main()
