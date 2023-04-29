#!/bin/bash

# Run PyInstaller with the --onefile option
pyinstaller --clean --onefile scripts/monitor.py --name dkp-monitor

# Clean up any unnecessary files
rm -rf build/
rm dkp-monitor.spec
