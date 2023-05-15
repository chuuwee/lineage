import os
import pickle
import requests
import sys
import tkinter as tk
import urllib
from get_events import get_events
from logger import get_logger
from login import login
from tkinter import filedialog

logger = get_logger('monitor')

def create_attendance_from_log(guest_log, event, cookies):
  event_name = guest_log.get('event_name')
  attendance_data = guest_log.get('attendance_data')
  encoded_attendance_data = urllib.parse.urlencode({
    'lanpartyid': event['id'],
    **attendance_data
  })

  url: str = 'http://lineageeq.dkpsystem.com/admineqdkpupload.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  logger.info('Uploading attendance, {}, {}'.format(event['id'], event_name))
  # send the request
  try:
    response = requests.post(url, cookies=cookies, headers=headers, data=encoded_attendance_data, allow_redirects=False, verify=False)
    response.raise_for_status()
    logger.info('Upload succeeded, {}'.format(event['id']))
  except Exception as err:
    logger.error('Upload failed, {}, {}'.format(event['id'], err))

def create_event_from_log(guest_log, cookies):
  event_date = guest_log.get('event_date')
  event_name = guest_log.get('event_name')
  event_data = guest_log.get('event_data')
  encoded_event_data = urllib.parse.urlencode(event_data)
  url: str = 'http://lineageeq.dkpsystem.com/editevent.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  logger.info('Creating event, {}'.format(event_name))
  # send the request
  requests.post(url, cookies=cookies, headers=headers, data=encoded_event_data, allow_redirects=False, verify=False)

  events = get_events()
  for event in events:
    if event['date'] == event_date and event['name'] == event_name:
      logger.info('Event created, {}'.format(event['id']))
      return event

  logger.error('Problem creating event, {}').format(event_name)
  raise ValueError("Check events page. Cannot find created event.")

def upload_guest_log(file_path):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  # Load the serialized cookies from a file
  with open(file_path, 'rb') as f:
    guest_log = pickle.load(f)

  event = create_event_from_log(guest_log, cookies)
  create_attendance_from_log(guest_log, event, cookies)

if __name__ == "__main__":
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  if not os.path.exists('cookies.pkl'):
    login()

  # create a Tkinter root window
  root = tk.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()

  upload_guest_log(file_path)