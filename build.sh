#!/bin/bash

# Run PyInstaller with the --onefile option
pyinstaller --clean --onefile scripts/main.py --name dkp-tools

# Clean up any unnecessary files
rm -rf build/
rm dkp-tools.spec