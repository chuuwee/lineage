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
from monitor import gen_raid_outcomes, gen_tail
from utils import debug_str, report_to_discord_guest, VERSION, get_purchase_from_item, report_purchase_to_discord_guest
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

def store_purchases(purchases, item, last_event, purchase_message_id):
  purchase = get_purchase_from_item(item)
  purchases = [*purchases, purchase]
  raw_pickle = {
    'event_sid': last_event['sid'] if last_event is not None else None,
    'event_name': last_event['name'] if last_event is not None else None,
    'purchases': purchases,
  }

  if last_event is not None:
    filename = get_filename(last_event)
  else:
    filename = '{}_noevent'.format(round(time.time()))

  # Add total number of purchases to the filename
  # TODO: Consider adding this to get_filename optionally
  filename = '{}_{}'.format(filename, len(purchases))

  purchase_message_id = report_purchase_to_discord_guest(purchases, filename, raw_pickle, last_event, purchase_message_id)
  return purchase_message_id, purchase

def store_attendance(event, attendance, debug):
  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  date_str = "{}/{}/{}".format(now.month, now.day, now.year)

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

def guest_monitor():
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
  if file_path is None or file_path == '':
    logger.info('No file selected, closing.')
    sys.exit()

  logger.info('Monitoring {}'.format(file_path))
  file_gen = gen_tail(file_path)

  purchases = []
  last_event = None
  purchase_message_id = None
  for (kind, message) in gen_raid_outcomes(file_gen):
    if kind == 'ATTENDANCE':
      purchase_message_id = None
      purchases = []
      event, attendance, debug = message
      last_event = event
      for name, attendee in attendance.items():
        logger.info('Confirmed {}, {}'.format(name, attendee))
      try:
        store_attendance(event, attendance, debug)
      except Exception as err:
        logger.error('Problem storing attendance, check log for issues and consider trying again, {}'.format(err))
    elif kind == "PURCHASE":
      item = message
      purchase_message_id, purchase = store_purchases(purchases, item, last_event, purchase_message_id)
      purchases.append(purchase)

if __name__ == "__main__":
  guest_monitor()