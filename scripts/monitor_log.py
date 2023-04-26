import re
import time
import tkinter as tk
from tkinter import filedialog
from utils import class_name_by_alias
from upload_attendance import upload_attendance

# create a Tkinter root window
root = tk.Tk()

# hide the main window
root.withdraw()

# show the file dialog and get the selected file path
file_path = filedialog.askopenfilename()

PATTERNS = {
  'DEFAULT': r"^\[.+?\] (?P<message>.+)",
  'ACTIVITY_SLASH_WHO': r"^.*\[(?P<level_class>\d+ [A-Za-z ]+|\bANONYMOUS\b)\].*? (?P<name>[A-Z][a-z]+)(?:.+\((?P<race>.+)\))?(?:.+\<(?P<guild>.+)\>)?",
  'ACTIVITY_START': r"^You say to your guild, '(?i:ELFSIM (?P<category>TARGET|LOCALE|EVENT)) (?P<name>.+)'",
  'ACTIVITY_GUILD': r"^You say to your guild, '(?i:ELFSIM \+GUILD) (?P<name>.+)'",
  'ACTIVITY_PILOT': r"^(?P<bot>[A-Z][a-z]+) tells you, '(?i:ELFSIM PILOT) (?P<pilot>[A-Za-z]+)'",
  'ACTIVITY_GUEST': r"^(?P<name>[A-Z][a-z]+) tells you, '(?i:ELFSIM GUEST)'"
}

def gen_tail(filename):
  with open(filename, "r") as f:
    f.seek(0, 2)

    while True:
      line = f.readline()

      if not line:
        time.sleep(1)
        continue

      yield line

def gen_messages(file_path):
  for line in gen_tail(file_path):
    log_match = re.match(PATTERNS['DEFAULT'], line)
    if log_match is None:
      continue

    message = log_match.group("message")
    if message is None:
      continue

    yield message

def gen_raid_activity(file_path):
  reading_activity = False
  reading_slash_who = False
  for message in gen_messages(file_path):
    if not reading_activity:
      start_match = re.match(PATTERNS["ACTIVITY_START"], message)
      if start_match is not None:
        reading_activity = True
        category, name = start_match.group("category", "name")
        yield ('START', { 'category': category.upper(), 'name': name })
      continue

    if message.startswith("There are"):
      reading_activity = False
      reading_slash_who = False
      yield ('END', None)
      continue
    elif message.startswith("Players on EverQuest:"):
      reading_slash_who = True
      continue
    elif reading_slash_who:
      if message.startswith('-'):
        continue

      slash_who_match = re.match(PATTERNS['ACTIVITY_SLASH_WHO'], message)
      if slash_who_match is None:
        continue

      name, level_class, guild = slash_who_match.group("name", "level_class", "guild")
      if level_class == "ANONYMOUS":
        level = None
        class_name = None
      else:
        level_str, alias = level_class.split(" ", 1)
        level = int(level_str)
        class_name = class_name_by_alias[alias]

      yield ('ATTENDEE', { 'name': name.capitalize(), 'level': level, 'class': class_name, 'guild': guild.upper() if guild else None })
      continue

    guild_match = re.match(PATTERNS['ACTIVITY_GUILD'], message)
    if guild_match is not None:
      name = guild_match.group("name")
      yield ('GUILD', { 'name': name.upper() })
      continue

    pilot_match = re.match(PATTERNS['ACTIVITY_PILOT'], message)
    if pilot_match is not None:
      pilot, bot = pilot_match.group("pilot", "bot")
      yield ('PILOT', { 'pilot': pilot.capitalize(), 'bot': bot.capitalize() })
      continue

    guest_match = re.match(PATTERNS['ACTIVITY_GUEST'], message)
    if guest_match is not None:
      name = guest_match.group("name")
      yield ('GUEST', { 'name': name.capitalize() })
      continue

def get_raid_attendance(pilots, guests, guilds, attendance):
  # Filter out entries for players not in guilds list
  raid_attendance = {
    player: attendance for player, attendance in attendance.items() if attendance.get('guild') in guilds
  }

  # Keep entries for guests in guests list
  for guest in guests:
    if guest not in raid_attendance:
      raid_attendance[guest] = attendance.get(guest, { 'name': guest, 'level': None, 'class': None, 'guild': None })

  # Remove bot from attendance entries for pilots
  for pilot_dict in pilots:
    bot, pilot = pilot_dict.get("bot"), pilot_dict.get("pilot")
    if bot in raid_attendance:
      raid_attendance.pop(bot)

    # If the bot isn't present, we're not including it in attendance
    if bot in attendance:
      # We build them like an anon user because they naturally should not be online
      raid_attendance[pilot] = { 'name': pilot, 'level': None, 'class': None, 'guild': None }

  return raid_attendance

def gen_raid_attendance(file_path):
  reading_attendance = False
  pilots = None
  guests = None
  guilds = None
  attendance = None
  event = None
  for (kind, message) in gen_raid_activity(file_path):
    if kind == 'START':
      pilots = []
      guests = []
      guilds = ['LINEAGE'] # Maybe set via CLI as the host guild
      event = message
      attendance = {}
      reading_attendance = True
    elif kind == 'END':
      yield (event, get_raid_attendance(pilots, guests, guilds, attendance))
      event = None
      pilots = None
      guests = None
      guilds = None
      attendance = None
      reading_attendance = False
    elif kind == 'ATTENDEE':
      name = message.get('name')
      attendance[name] = message
    elif kind == 'PILOT':
      pilots.append(message)
    elif kind == 'GUEST':
      guests.append(message.get('name'))
    elif kind == 'GUILD':
      guilds.append(message.get('name'))

if __name__ == "__main__":
  for event, attendance in gen_raid_attendance(file_path):
    for name, attendee in attendance.items():
      continue
    upload_attendance(event, attendance)