import os
import pickle
import sys
import tkinter as tk
from login import login
from tkinter import filedialog

def peek_guest_log(file_path):
  # Load the serialized cookies from a file
  with open(file_path, 'rb') as f:
    guest_log = pickle.load(f)

  print('[DATE]\n{}'.format(guest_log.get('event_date').strftime("%B %d, %Y at %I:%M %p")))
  print('[NAME]\n{}'.format(guest_log.get('event_name')))
  attendance_data = guest_log.get('attendance_data')
  print('[DKP]\n{}'.format(attendance_data.get('points')))
  print('[SUMMARY]\n{}'.format(attendance_data.get('description')))

if __name__ == "__main__":
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  if not login():
    sys.exit()

  # create a Tkinter root window
  root = tk.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()

  peek_guest_log(file_path)