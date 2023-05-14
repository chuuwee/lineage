import os
import re
import sys
import time
import tkinter as tk
from tkinter import filedialog
from utils import class_name_by_alias
from upload import upload_attendance
from logger import get_logger
from login import login

logger = get_logger('monitor')

PATTERNS = {
  'DEFAULT': r"^\[.+?\] (?P<message>.+)",
  'ACTIVITY_SLASH_WHO': r"^.*\[(?P<level_class>\d+ [A-Za-z ]+|\bANONYMOUS\b)\].*? (?P<name>[A-Z][a-z]+)(?:.+\((?P<race>.+)\))?(?:.+\<(?P<guild>.+)\>)?",
  'ACTIVITY_START': r"^You say to your guild, '(?i:\+(?P<category>TARGET|LOCALE|EVENT)) (?P<dkp>\d+ )?(?P<name>.+)'",
  'ACTIVITY_GUILD': r"^You say to your guild, '(?i:\+GUILD) (?P<name>.+)'",
  'ACTIVITY_PILOT': r"^(?P<bot>[A-Z][a-z]+) tells you, '(?i:\+PILOT) (?P<pilot>[A-Za-z]+)'",
  'ACTIVITY_PILOT_ALTERNATE': r"^(?P<bot>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+PILOT) (?P<pilot>[A-Za-z]+)",
  'ACTIVITY_PILOT_GUILD': r"^(?P<bot>[A-Z][a-z]+) tells the guild, '(?i:\+PILOT) (?P<pilot>[A-Za-z]+)'",
  'ACTIVITY_GUEST': r"^(?P<name>[A-Z][a-z]+) tells you, '(?i:\+GUEST)'",
  'ACTIVITY_GUEST_ALTERNATE': r"^(?P<name>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+GUEST)",
  'ACTIVITY_ABSENT': r"^(?P<name>[A-Z][a-z]+) tells you, '(?i:\+ABSENT)( (?P<pilot>[A-Za-z]+))?'",
  'ACTIVITY_ABSENT_ALTERNATE': r"^(?P<name>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+ABSENT)( (?P<pilot>[A-Za-z]+))?",
  'ACTIVITY_ABSENT_GUILD': r"^(?P<name>[A-Z][a-z]+) tells the guild, '(?i:\+ABSENT)( (?P<pilot>[A-Za-z]+))?'",
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
        category, name, dkp = start_match.group("category", "name", "dkp")
        yield ('START', { 'category': category.upper(), 'name': name, 'dkp': int(dkp) if dkp is not None else 1 })
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

    pilot_match_alternate = re.match(PATTERNS['ACTIVITY_PILOT_ALTERNATE'], message)
    if pilot_match_alternate is not None:
      pilot, bot = pilot_match_alternate.group("pilot", "bot")
      yield ('PILOT', { 'pilot': pilot.capitalize(), 'bot': bot.capitalize() })
      continue

    pilot_match_guild = re.match(PATTERNS['ACTIVITY_PILOT_GUILD'], message)
    if pilot_match_guild is not None:
      pilot, bot = pilot_match_guild.group("pilot", "bot")
      yield ('PILOT', { 'pilot': pilot.capitalize(), 'bot': bot.capitalize() })
      continue

    guest_match = re.match(PATTERNS['ACTIVITY_GUEST'], message)
    if guest_match is not None:
      name = guest_match.group("name")
      yield ('GUEST', { 'name': name.capitalize() })
      continue

    guest_match_alternate = re.match(PATTERNS['ACTIVITY_GUEST_ALTERNATE'], message)
    if guest_match_alternate is not None:
      name = guest_match_alternate.group("name")
      yield ('GUEST', { 'name': name.capitalize() })
      continue

    absent_match = re.match(PATTERNS['ACTIVITY_ABSENT'], message)
    if absent_match is not None:
      name, pilot = absent_match.group("name", "pilot")
      yield ('ABSENT', { 'name': name.capitalize(), 'pilot': pilot.capitalize() if pilot else None })
      continue

    absent_match_alternate = re.match(PATTERNS['ACTIVITY_ABSENT_ALTERNATE'], message)
    if absent_match_alternate is not None:
      name, pilot = absent_match_alternate.group("name", "pilot")
      yield ('ABSENT', { 'name': name.capitalize(), 'pilot': pilot.capitalize() if pilot else None })
      continue

    absent_match_guild = re.match(PATTERNS['ACTIVITY_ABSENT_GUILD'], message)
    if absent_match_guild is not None:
      name, pilot = absent_match_guild.group("name", "pilot")
      yield ('ABSENT', { 'name': name.capitalize(), 'pilot': pilot.capitalize() if pilot else None })
      continue

def get_raid_attendance(pilots, guests, guilds, absentees, attendance):
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
  
  for absentee_dict in absentees:
    name, pilot = absentee_dict.get("name"), absentee_dict.get("pilot")
    name = name if pilot is None else pilot
    raid_attendance[name] = { 'name': name, 'level': None, 'class': None, 'guild': None }

  return raid_attendance

def format_absentee(absentee):
  name, pilot = absentee.get('name'), absentee.get('pilot')
  if pilot is None:
    return name
  return '{}/{}'.format(pilot, name) 

def debug_string(pilots, guests, guilds, absentees, attendance, raid_attendance):
  return 'RAID\n{}\nPILOT/BOTS\n{}\nGUESTS\n{}\nABSENTEES/BOTS\n{}\nGUILDS\n{}\nWHO\n{}\n'.format(
    '\n'.join(sorted(['  {}'.format(name) for name, attendee in raid_attendance.items()])),
    '\n'.join(sorted(['  {}/{}'.format(pilot.get('pilot'), pilot.get('bot')) for pilot in pilots])),
    '\n'.join(sorted(['  {}'.format(guest) for guest in guests])),
    '\n'.join(sorted(['  {}'.format(format_absentee(absentee)) for absentee in absentees])),
    '\n'.join(sorted(['  {}'.format(guild) for guild in guilds])),
    '\n'.join(sorted(['  {}'.format(name) for name, attendee in attendance.items()])),
  )

def gen_raid_attendance(file_path):
  event = None
  pilots = None
  guests = None
  guilds = None
  absentees = None
  attendance = None
  for (kind, message) in gen_raid_activity(file_path):
    logger.info('{}, {}'.format(kind, message))
    if kind == 'START':
      event = message
      pilots = []
      guests = []
      guilds = ['LINEAGE'] # Maybe set via CLI as the host guild
      absentees = []
      attendance = {}
    elif kind == 'END':
      raid_attendance = get_raid_attendance(pilots, guests, guilds, absentees, attendance)
      debug = debug_string(pilots, guests, guilds, absentees, attendance, raid_attendance)
      yield (event, raid_attendance, debug)
      event = None
      pilots = None
      guests = None
      guilds = None
      absentees = None
      attendance = None
    elif kind == 'ATTENDEE':
      name = message.get('name')
      attendance[name] = message
    elif kind == 'PILOT':
      pilots.append(message)
    elif kind == 'GUEST':
      guests.append(message.get('name'))
    elif kind == 'GUILD':
      guilds.append(message.get('name'))
    elif kind == 'ABSENT':
      absentees.append(message)

if __name__ == "__main__":
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  if not os.path.exists('cookies.pkl'):
    login()

  # create a Tkinter root window
  root = tk.Tk()

  # hide the main window
  root.withdraw()

  # show the file dialog and get the selected file path
  file_path = filedialog.askopenfilename()

  for event, attendance, debug in gen_raid_attendance(file_path):
    for name, attendee in attendance.items():
      logger.info('Confirmed {}, {}'.format(name, attendee))
    upload_attendance(event, attendance, debug)
