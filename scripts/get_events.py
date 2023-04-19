import requests
import pickle
from bs4 import BeautifulSoup

# Load the serialized cookies from a file
with open('cookies.pkl', 'rb') as f:
  cookies = pickle.load(f)

# Make a GET request to the site with the loaded cookies
response = requests.get('http://lineageeq.dkpsystem.com/admineventcategory.php', cookies=cookies)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the name and identifier values
table_rows = soup.css.select('table.list tr')
data = []
for row in table_rows[2:]:
    name = row.css.select('td')[1].text.strip()
    identifier = int(row.css.select('a')[0].attrs['href'].split('=')[1])
    data.append({'name': name, 'id': identifier})

# Print the extracted data
for item in data:
    print(item['name'], item['id'])
