import os
import pickle
import pytz
import requests
import sys
import tkinter as tk
import urllib
from get_event_id import get_event_id
from get_item_id import get_item_id
from get_member_id import get_member_id
from utils import get_webhook_url, report_purchase_to_discord
from logger import get_logger
from login import login
from tkinter import filedialog
from discord_webhook import DiscordWebhook
import pdb

logger = get_logger('guest_purchase_upload')

def upload_guest_purchase_log(file_path):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  with open(file_path, 'rb') as f:
    guest_purchase_log = pickle.load(f)

  webhook_url = get_webhook_url()
  if webhook_url is None:
    logger.info('No webhook.url file found. See README.md to send Discord reports.')
    return

  event_sid = guest_purchase_log.get('event_sid')
  event_name = guest_purchase_log.get('event_name')
  purchases = guest_purchase_log.get('purchases')
  message_id = guest_purchase_log.get('message_id')

  url: str = 'http://lineageeq.dkpsystem.com/editdkpmemberitem.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  event_id = get_event_id(event_sid) if event_sid is not None else None
  for purchase in purchases:
    member_id = get_member_id(purchase['name'])
    item_id = get_item_id(purchase['item'])

    # set the form data for the request
    data = urllib.parse.urlencode({
      'lanpartyid': event_id if event_id is not None else '',
      'daytext': purchase['date_str'],
      'dkpsystemid': 1,
      'memberid': member_id,
      'newitem': purchase['item'] if item_id is None else '',
      'dkpitemid': item_id if item_id is not None else '',
      'points': purchase['dkp'],
    })

    logger.info('Uploading purchase, {}, {}'.format(data, message_id))
    # send the request
    try:
      response = requests.post(url, cookies=cookies, headers=headers, data=data, allow_redirects=False, verify=False)
      response.raise_for_status()
    except Exception as err:
      logger.error('Upload failed, {}, {}'.format(data, message_id))

  pdb.set_trace()
  if message_id is not None and webhook_url is not None:
    wh = DiscordWebhook(url=webhook_url, id=message_id)
    try:
      logger.info('Deleting original guest purchase report {}'.format(message_id))
      wh.delete()
    except Exception as err:
      logger.info('Error deleting guest report on Discord'.format(message_id))

  report_purchase_to_discord(purchases, { 'name': event_name }, None)

def upload_grats_file(file_path):
  if file_path is None:
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

  logger.info('Preparing to upload {}'.format(file_path))

  try:
    upload_guest_purchase_log(file_path)
  except Exception as err:
    logger.error('Problem uploading attendance, check log for issues and consider trying again, {}'.format(err))

if __name__ == "__main__":
  upload_grats_file()