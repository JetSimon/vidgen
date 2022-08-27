#!/bin/bash
# Change directory to be where the command is.
cd "$(cd "$(dirname "$0")" > /dev/null && pwd)"
python3 gui.py