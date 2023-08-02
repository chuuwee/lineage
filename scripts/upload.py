from datetime import datetime
import pickle
import pytz
import requests
import urllib.parse
from get_event_id import get_event_id
from get_item_id import get_item_id
from get_member_id import get_member_id
from utils import debug_str, report_to_discord, report_purchase_to_discord, get_purchase_from_item
from create_event import create_event
from logger import get_logger
from constants import DKP_SCRIPT_VERSION_TAG

logger = get_logger('upload')

def get_raid_attendance_payload(attendance):
  char_payload = {}
  for index, (name, char_info) in enumerate(attendance.items()):
    char_payload['playername[{:d}]'.format(index)] = name
    char_payload['class[{:d}]'.format(index)] = char_info['class'] if not None else ''
    char_payload['race[{:d}]'.format(index)] = ''
    char_payload['level[{:d}]'.format(index)] = char_info['level'] if not None else 1
    char_payload['raidmember[{:d}]'.format(index)] = 0
    char_payload['altmember[{:d}]'.format(index)] = ''
    char_payload['indivpoints[{:d}]'.format(index)] = ''
  return char_payload

def upload_purchase(purchases, item, last_event, message_id):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  date_str = "{}/{}/{}".format(now.month, now.day, now.year)

  url: str = 'http://lineageeq.dkpsystem.com/editdkpmemberitem.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  member_id = get_member_id(item['name'])
  item_id = get_item_id(item['item'])
  event_id = get_event_id(last_event['sid']) if last_event is not None else None

  # set the form data for the request
  data = urllib.parse.urlencode({
    'lanpartyid': event_id if event_id is not None else '',
    'daytext': date_str,
    'dkpsystemid': 1,
    'memberid': member_id,
    'newitem': item['item'] if item_id is None else '',
    'dkpitemid': item_id if item_id is not None else '',
    'points': item['dkp'],
  })

  purchase = get_purchase_from_item(item)
  purchases = [*purchases, purchase]

  logger.info('Uploading purchase, {}, {}'.format(data, message_id))
  # send the request
  try:
    response = requests.post(url, cookies=cookies, headers=headers, data=data, allow_redirects=False, verify=False)
    response.raise_for_status()
    purchase_message_id = report_purchase_to_discord(purchases, last_event, message_id)
    return purchase_message_id, purchase
  except Exception as err:
    logger.error('Upload failed, {}, {}'.format(data, message_id))

def upload_attendance(event, attendance, debug):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  date_str = now.strftime("%M/%D/%Y").lower()

  url: str = 'http://lineageeq.dkpsystem.com/admineqdkpupload.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  event_ = create_event(event)
  char_payload = get_raid_attendance_payload(attendance)

  # set the form data for the request
  data = urllib.parse.urlencode({
    'server': 'P99 Green',
    'lanpartyid': event_['id'],
    'date': date_str,
    'dkpsystemid': 1,
    'pointtype': 'straight',
    'points': event['dkp'],
    'description': '{}\n{}'.format(debug_str(**debug), DKP_SCRIPT_VERSION_TAG),
    'process': 'Submit This Raid',
    'game': 'eq',
    **char_payload
  })

  logger.info('Uploading attendance, {}'.format(event_['id']))
  # send the request
  try:
    response = requests.post(url, cookies=cookies, headers=headers, data=data, allow_redirects=False, verify=False)
    response.raise_for_status()
    report_to_discord(event['name'], now, event['dkp'], event_['id'], debug)
    logger.info('Upload succeeded, {} dkp, {} attendees, {}'.format(event['dkp'], len(attendance.keys()), event_['id']))
  except Exception as err:
    logger.error('Upload failed, {}, {}'.format(event_['id'], err))
