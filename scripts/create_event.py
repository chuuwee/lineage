from datetime import datetime
import pickle
import pytz
import requests
import urllib.parse
from get_event_categories import get_event_categories, print_event_category
from get_events import get_events, print_event
from constants import CATEGORY_ID_BY_CATEGORY
from logger import get_logger
from constants import DKP_SCRIPT_VERSION_TAG

logger = get_logger('create_event')

def create_event(config, live = True):
  logger.info('Invoking create event, {}'.format(config))
  if live and config is None:
    event_categories = get_event_categories()
    for event_category in event_categories:
      print_event_category(event_category)

    event_category_id_raw: str = input('select an event type: ')
    if not event_category_id_raw.isdigit():
      raise ValueError('Invalid category id')
    event_category_id = int(event_category_id_raw)
    event_name: str = input('name your event: ')
  elif config is not None:
    event_category_id = CATEGORY_ID_BY_CATEGORY.get(config.get('category'))
    event_name = config.get('name')
  else:
    raise ValueError('Problem creating event')

  if live:
    # Load the serialized cookies from a file
    with open('cookies.pkl', 'rb') as f:
      cookies = pickle.load(f)

  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  time_str = now.strftime("%m/%d/%Y %I:%M%p").lower()

  # We parse this for downstream comparison. Truncates off seconds
  time_obj = datetime.strptime(time_str, '%m/%d/%Y %I:%M%p')

  url: str = 'http://lineageeq.dkpsystem.com/editevent.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  # set the form data for the request
  data = {
    'eventcategoryid': event_category_id,
    'game': 'eq',
    'lanparty': event_name,
    'securitylevelid': 5,
    'rosterid': 1,
    'signupsecuritylevelid': 5,
    'day': time_str,
    'description': DKP_SCRIPT_VERSION_TAG,
    'submit': 'Submit',
  }

  if live:
    encoded_data = urllib.parse.urlencode(data)
    logger.info('Creating event, {}, {}'.format(event_category_id, event_name))
    # send the request
    response = requests.post(url, cookies=cookies, headers=headers, data=encoded_data, allow_redirects=False, verify=False)

    events = get_events()
    for event in events:
      if event['date'] == time_obj and event['name'] == event_name:
        logger.info('Event created, {}'.format(event['id']))
        return event

    logger.error('Problem creating event, {}, {}'.format(event_category_id, event_name))
    raise ValueError("Check events page. Cannot find created event.")
  else:
    return (time_obj, event_name, data)

if __name__ == "__main__":
  event = create_event()
  print_event(event)

