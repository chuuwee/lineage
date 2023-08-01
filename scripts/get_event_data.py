import requests
import pickle
from datetime import datetime
from bs4 import BeautifulSoup
import pdb

def get_sid(event_name):
  fragments = event_name.rsplit(' ', 1)
  if len(fragments) == 2:
    return fragments[1].strip('()')
  else:
    return None

def get_event_data(event_id):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  response = requests.get('http://lineageeq.dkpsystem.com/eventdetails.php?id={}'.format(event_id), cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract the name and identifier values

  select_options = soup.css.select('tr.list1 select option')
  dkpraidid_list = [int(opt['value']) for opt in select_options if 'Attendees)' in opt.text]
  if len(dkpraidid_list) == 0:
    # Handle this
    return
  
  dkpraidid = dkpraidid_list[0]

  response = requests.get('http://lineageeq.dkpsystem.com/raiddetails.php?dkpraidid={}'.format(dkpraidid), cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')
  tr_list = soup.css.select('.list tr.list2')
  return dkpraidid, ''.join([tr.text for tr in tr_list])

if __name__ == "__main__":
  name = input('event id: ')
  print(get_event_data(name.strip()))
