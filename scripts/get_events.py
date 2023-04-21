import requests
import pickle
from datetime import datetime
from bs4 import BeautifulSoup

def get_events():
# Load the serialized cookies from a file
  with open('cookies.pkl', 'rb') as f:
    cookies = pickle.load(f)

# Make a GET request to the site with the loaded cookies
  response = requests.get('http://lineageeq.dkpsystem.com/adminevent.php', cookies=cookies)
  soup = BeautifulSoup(response.text, 'html.parser')

# Extract the name and identifier values
  table_rows = soup.css.select('#lanCurrent tr')
  data = []
  for row in table_rows[3:]:
    tds = row.css.select('td')
    date_str = tds[0].text.strip()
    date_obj = datetime.strptime(date_str, '%m/%d/%y %I:%M%p')
    category_name = tds[1].text.strip()
    event_name = tds[2].text.strip()
    identifier = int(row.css.select('a')[0].attrs['href'].split('=')[1])
    data.append({
      'date': date_obj,
      'category_name': category_name,
      'name': event_name,
      'id': identifier,
    })

  return data

def print_event(event):
  date_str = datetime.strftime(event['date'], '%m/%d/%y %I:%M%p').lower()
  print('{: >2} - {} - {} - {}'.format((event['id']), date_str, event['category_name'], event['name']))

if __name__ == "__main__":
  events = get_events()
  for event in events:
    print_event(event)
