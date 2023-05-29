import os
import requests
import pickle
import urllib.parse
from get_events import get_events
from getpass import getpass
from logger import get_logger

logger = get_logger('login')

def is_login_valid():
  try:
    events = get_events()
    return len(events) > 0
  except Exception as err:
    return False

def login_():
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

def login():
  while True:
    if not os.path.exists('cookies.pkl'):
      try:
        login_()
      except Exception as err:
        logger.error('Error on login, {}'.format(err))
      except (SystemExit, KeyboardInterrupt) as err:
        logger.info('Exiting...')
        break

    if is_login_valid():
      return True
    else:
      logger.error('Problem encountered logging in. Try again or check the site.')
      try:
        if os.path.exists('cookies.pkl'):
          logger.info('Removing cookies file')
          os.remove('cookies.pkl')
      except Exception as err:
        logger.error('Problem encountered removing cookies file, {}', err)
  return False

if __name__ == "__main__":
  login()