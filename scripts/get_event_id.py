import requests
import pickle
from datetime import datetime
from bs4 import BeautifulSoup

def get_sid(event_name):
  fragments = event_name.rsplit(' ', 1)
  if len(fragments) == 2:
    return fragments[1].strip('()')
  else:
    return None

def get_event_id(sid):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  response = requests.get('http://lineageeq.dkpsystem.com/editdkpmemberitem.php', cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract the name and identifier values
  events = soup.css.select('select[name="lanpartyid"] option')
  event_ids = [event['value'] for event in events if get_sid(event.get_text()) == sid]
  if len(event_ids) == 1:
    return int(event_ids[0])
  else:
    return None

if __name__ == "__main__":
  name = input('event sid: ')
  print(get_event_id(name.strip()))
