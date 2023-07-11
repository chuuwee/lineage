import requests
import pickle
from datetime import datetime
from bs4 import BeautifulSoup

def get_item_id(item_name):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  response = requests.get('http://lineageeq.dkpsystem.com/editdkpmemberitem.php', cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract the name and identifier values
  items = soup.css.select('select[name="dkpitemid"] option')
  item_ids = [item['value'] for item in items if item.get_text() == item_name]
  if len(item_ids) > 0:
    return int(item_ids[0])
  else:
    return None

if __name__ == "__main__":
  name = input('item name: ')
  print(get_item_id(name.strip()))
