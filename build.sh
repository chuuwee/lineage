#!/bin/bash

# Run PyInstaller with the --onefile option
pyinstaller --clean --onefile scripts/monitor.py --name dkp-monitor
pyinstaller --clean --onefile scripts/guest_monitor.py --name dkp-monitor-guest
pyinstaller --clean --onefile scripts/upload_guest_log.py --name dkp-upload
pyinstaller --clean --onefile scripts/peek_guest_log.py --name dkp-peek

# Clean up any unnecessary files
rm -rf build/
rm dkp-monitor.spec
rm dkp-monitor-guest.spec
rm dkp-upload.spec
rm dkp-peek.spec
