import os
import pickle
import sys
import tkinter as tk
from login import login
from tkinter import filedialog
from logger import get_logger

logger = get_logger('peek_guest_log')

def peek_guest_log(file_path):
  # Load the serialized cookies from a file
  with open(file_path, 'rb') as f:
    guest_log = pickle.load(f)

  print('[DATE]\n{}'.format(guest_log.get('event_date').strftime("%B %d, %Y at %I:%M %p")))
  print('[NAME]\n{}'.format(guest_log.get('event_name')))
  attendance_data = guest_log.get('attendance_data')
  print('[DKP]\n{}'.format(attendance_data.get('points')))
  print('[SUMMARY]\n{}'.format(attendance_data.get('description')))

def view_raid_file():
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  # create a Tkinter root window
  root = tk.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()
  if file_path is None or file_path == '':
    logger.info('No file selected, closing.')
    sys.exit()

  try:
    peek_guest_log(file_path)
  except Exception as err:
    logger.error('Problem uploading attendance, check log for issues and consider trying again, {}'.format(err))

if __name__ == "__main__":
  view_raid_file()