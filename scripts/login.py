import requests
import pickle
from getpass import getpass
import urllib.parse

def login():
  # set the url and headers for the request
  url: str = 'http://lineageeq.dkpsystem.com/login.php'
  headers: dict[str, str] = {
    'content-type': 'application/x-www-form-urlencoded',
  }

  # prompt the user for login and password
  login: str = input('enter your login: ')
  password: str = getpass('enter your password: ')

  # set the form data for the request
  data = urllib.parse.urlencode({
    'login': login,
    'password': password,
    'submit': 'log in',
    'email': ''
  })

  # send the request and store the cookies in a file
  response = requests.post(url, headers=headers, data=data, allow_redirects=False, verify=False)

  if len(response.cookies) == 1:
    raise ValueError('Invalid password')

  # serialize the cookies to a file
  with open('cookies.pkl', 'wb') as f:
    pickle.dump(response.cookies, f)

if __name__ == "__main__":
  login()