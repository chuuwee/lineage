# Example raid log payload:
#
# [Tue Apr 11 19:57:50 2023] Players on EverQuest:
# [Tue Apr 11 19:57:50 2023] ---------------------------
# [Tue Apr 11 19:57:50 2023] [56 Blackguard] Lorem (Gnome) <Duis Fermentum>
# [Tue Apr 11 20:01:55 2023]  AFK [60 Oracle] Ipsum (Ogre) <Duis Fermentum>
# [Tue Apr 11 19:57:50 2023] [57 Blackguard] Dolor (Dwarf) <Venanatis>
# [Tue Apr 11 20:01:55 2023] [57 Luminary] Sit (Bear) <Venanatis> LFG
# [Tue Apr 11 20:01:55 2023] [ANONYMOUS] Amet
# [Tue Apr 11 20:01:55 2023] [ANONYMOUS] Consectetur <Laoreet>
# [Tue Apr 11 19:57:50 2023] There are 2 players in Temple of Veeshan.

import re
import time
import tkinter as tk
from tkinter import filedialog
from utils import class_name_by_alias

# create a Tkinter root window
root = tk.Tk()

# hide the main window
root.withdraw()

# show the file dialog and get the selected file path
file_path = filedialog.askopenfilename()

PATTERNS = {
  'DEFAULT': r"^\[.+?\] (?P<message>.+)",
  'RAID_NAMED': r"^.*\[(?P<level_class>\d+ [A-Za-z]+|\bANONYMOUS\b)\].*? (?P<name>[A-Z][a-z]+)(?:.+\((?P<race>.+)\))?(?:.+\<(?P<guild>.+)\>)?",
}

def tail(filename):
  with open(filename, "r") as f:
    f.seek(0, 2)

    while True:
      line = f.readline()

      if not line:
        time.sleep(1)
        continue

      yield line

def parse_log(file_path):
  raid_log_started = False
  raid_log_ended = False
  skip_line = 0
  raid_attendees = {}
  for line in tail(file_path):
    if raid_log_ended:
      break

    if skip_line:
      skip_line -= 1
      continue

    log_match = re.match(PATTERNS['DEFAULT'], line)
    if log_match is None:
      continue

    message = log_match.group("message")
    if raid_log_started:
      raid_log_ended = message.startswith("There are ")
      if raid_log_ended:
        return raid_attendees
      else:
        raid_log_match = re.match(PATTERNS['RAID_NAMED'], message)
        if raid_log_match is None:
          continue

        name, race, level_class, guild = raid_log_match.group("name", "race", "level_class", "guild")
        if level_class == "ANONYMOUS":
          level = 1
          class_name = None
        else:
          level_str, alias = level_class.split()
          level = int(level_str)
          class_name = class_name_by_alias[alias]

        raid_attendees[name] = {
          'race': race,
          'level': level,
          'class': class_name,
          'guild': guild,
        }
    else:
      raid_log_started = message.startswith('Players on EverQuest:')
      skip_line += 1

def get_raid_attendance_payload():
  raid_attendance = parse_log(file_path)

  char_payload = {}
  for index, (name, char_info) in enumerate(raid_attendance.items()):
    char_payload['playername'.format(index)] = name
    char_payload['class[{:d}]'.format(index)] = char_info['class'] if not None else ''
    char_payload['race[{:d}]'.format(index)] = char_info['race'] if not None else ''
    char_payload['race[{:d}]'.format(index)] = ''
    char_payload['level[{:d}]'.format(index)] = char_info['level']
    char_payload['raidmember[{:d}]'.format(index)] = 0
    char_payload['altmember[{:d}]'.format(index)] = ''
    char_payload['indivpoints[{:d}]'.format(index)] = ''

  return char_payload

if __name__ == "__main__":
  payload = get_raid_attendance_payload()
  print(payload)

