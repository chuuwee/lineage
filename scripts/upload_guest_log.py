import os
import pickle
import pytz
import requests
import sys
import tkinter as tk
import urllib
from upload_guest_purchases import upload_grats_file
from utils import report_to_discord, get_webhook_url
from get_events import get_events
from logger import get_logger
from login import login
from tkinter import filedialog
from discord_webhook import DiscordWebhook

logger = get_logger('guest_upload')

def create_attendance_from_log(guest_log, event, cookies):
  webhook_url = get_webhook_url()
  if webhook_url is None:
    logger.info('No webhook.url file found. See README.md to send Discord reports.')
    return

  event_name = guest_log.get('event_name')
  event_date = guest_log.get('event_date')
  attendance_data = guest_log.get('attendance_data')
  dkp = attendance_data.get('points')
  encoded_attendance_data = urllib.parse.urlencode({
    'lanpartyid': event['id'],
    **attendance_data
  })

  url: str = 'http://lineageeq.dkpsystem.com/admineqdkpupload.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  # Localize before sending to Discord
  central = pytz.timezone('US/Central')
  localized_date = central.localize(event_date)

  logger.info('Uploading attendance, {}, {}'.format(event['id'], event_name))
  # send the request
  try:
    response = requests.post(url, cookies=cookies, headers=headers, data=encoded_attendance_data, allow_redirects=False, verify=False)
    response.raise_for_status()
    debug = guest_log.get('debug')
    message_id = guest_log.get('message_id')
    if message_id is not None and webhook_url is not None:
      wh = DiscordWebhook(url=webhook_url, id=message_id)
      try:
        logger.info('Deleting original guest report {}'.format(message_id))
        wh.delete()
      except Exception as err:
        logger.info('Error deleting guest report on Discord'.format(message_id))
    report_to_discord(event_name, localized_date, dkp, event['id'], debug)
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

def upload_raid_file():
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  if not login():
    sys.exit()

  # create a Tkinter root window
  root = tk.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()
  if file_path is None or file_path == '':
    logger.info('No file selected, closing.')
    sys.exit()

  if file_path.endswith('.grats'):
    return upload_grats_file(file_path)

  logger.info('Preparing to upload {}'.format(file_path))

  try:
    upload_guest_log(file_path)
  except Exception as err:
    logger.error('Problem uploading attendance, check log for issues and consider trying again, {}'.format(err))

if __name__ == "__main__":
  upload_raid_file()