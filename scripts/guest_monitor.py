import os
import pickle
import re
import sys
import pytz
import time
import tkinter
from constants import DKP_SCRIPT_VERSION_TAG
from create_event import create_event
from datetime import datetime
from logger import get_logger
from tkinter import filedialog
from monitor import gen_raid_attendance
from utils import debug_str, report_to_discord_guest, VERSION
from upload import get_raid_attendance_payload

logger = get_logger('guest_monitor')

def process_string(s):
    # Replace spaces with underscores
    s = s.replace(' ', '_')
    
    # Remove all non-alphanumeric characters and underscores
    s = re.sub(r'[^a-zA-Z0-9_]', '', s)
    
    return s

def get_filename(event):
  category, name = event.get('category').lower(), event.get('name').lower()
  return '{}_{}_{}'.format(round(time.time()), category, process_string(name))

def store_attendance(event, attendance, debug):
  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  date_str = now.strftime("%M/%D/%Y").lower()

  (event_date, event_name, event_) = create_event(event, live=False)
  char_payload = get_raid_attendance_payload(attendance)

  # set the form data for the request
  data = {
    'server': 'P99 Green',
    'date': date_str,
    'dkpsystemid': 1,
    'pointtype': 'straight',
    'points': event['dkp'],
    'description': '{}\n{}'.format(debug_str(**debug), DKP_SCRIPT_VERSION_TAG),
    'process': 'Submit This Raid',
    'game': 'eq',
    **char_payload
  }

  filename = get_filename(event)

  raw_pickle = {
    'event_date': event_date,
    'event_name': event_name,
    'event_data': event_,
    'attendance_data': data,
    'debug': debug,
    'version': VERSION,
  }
  report_to_discord_guest(event_name, now, event['dkp'], filename, raw_pickle, debug)

if __name__ == "__main__":
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  # create a Tkinter root window
  root = tkinter.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()

  for event, attendance, debug in gen_raid_attendance(file_path):
    for name, attendee in attendance.items():
      logger.info('Confirmed {}, {}'.format(name, attendee))
    store_attendance(event, attendance, debug)