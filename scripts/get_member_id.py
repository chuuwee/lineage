import requests
import pickle
from datetime import datetime
from bs4 import BeautifulSoup

def get_member_id(name):
  # Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

  name_formatted = name.capitalize()
  response = requests.get('http://lineageeq.dkpsystem.com/editdkpmemberitem.php', cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')

  # Extract the name and identifier values
  members = soup.css.select('select[name="memberid"] option')
  member_ids = [member['value'] for member in members if member.get_text().split(' ', 1)[0] == name_formatted]
  if len(member_ids) == 1:
    return int(member_ids[0])
  else:
    return None

if __name__ == "__main__":
  name = input('member name: ')
  print(get_member_id(name.strip()))
