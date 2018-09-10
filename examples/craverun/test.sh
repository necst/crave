#!/bin/bash
rm -rf sample
python craverun.py --debug sample load sample.json
python craverun.py --debug sample craft
python craverun.py --debug sample scan
python craverun.py --debug sample infer
