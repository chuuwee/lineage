import os
import re
import sys
import time
import tkinter as tk
from tkinter import filedialog
from utils import debug_obj, debug_str, class_name_by_alias, get_webhook_url, get_sid, report_purchase_to_discord
from upload import upload_attendance, upload_purchase
from get_events import get_events
from logger import get_logger
from login import login
from typing import Set, Dict, Optional

logger = get_logger('monitor')

PATTERNS = {
  'DEFAULT': r"^\[.+?\] (?P<message>.+)",
  'ACTIVITY_SLASH_WHO': r"^.*\[(?P<level_class>\d+ [A-Za-z ]+|\bANONYMOUS\b)\].*? (?P<name>[A-Z][a-z]+)(?:.+\((?P<race>.+)\))?(?:.+\<(?P<guild>.+)\>)?",
  'ACTIVITY_START': r"^You say to your guild, '(?i:\+(?P<category>TARGET|LOCALE|EVENT)) (?P<dkp>\d+ )?(?P<name>.+)'",
  'ACTIVITY_GUILD': r"^You say to your guild, '(?i:\+GUILD) (?P<name>.+)'",
  'ACTIVITY_PILOT': r"^(?P<bot>[A-Z][a-z]+) tells you, '(?i:\+PILOT) (?P<pilot>[A-Za-z]+)'",
  'ACTIVITY_PILOT_ALTERNATE': r"^(?P<bot>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+PILOT) (?P<pilot>[A-Za-z]+)",
  'ACTIVITY_PILOT_GUILD': r"^(?P<bot>[A-Z][a-z]+) tells the guild, '(?i:\+PILOT) (?P<pilot>[A-Za-z]+)'",
  'ACTIVITY_PILOT_SELF': r"(?P<bot>[A-Z][a-z]+) (?i:\+PILOT) (?P<pilot>[A-Z][a-z]+)",
  'ACTIVITY_GUEST': r"^(?P<name>[A-Z][a-z]+) tells you, '(?i:\+GUEST)'",
  'ACTIVITY_GUEST_ALTERNATE': r"^(?P<name>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+GUEST)",
  'ACTIVITY_ABSENT': r"^(?P<name>[A-Z][a-z]+) tells you, '(?i:\+ABSENT)'",
  'ACTIVITY_ABSENT_ALTERNATE': r"^(?P<name>[A-Z][a-z]+) -> [A-z][a-z]+: (?i:\+ABSENT)",
  'ACTIVITY_ABSENT_GUILD': r"^(?P<name>[A-Z][a-z]+) tells the guild, '(?i:\+ABSENT)'",
  'ACTIVITY_SYSTEM_TEST': r"(?P<self>[A-Z][a-z]+) (?i:\+TEST)",
  'ACTIVITY_CANCEL': r"(?P<self>[A-Z][a-z]+) (?i:\+CANCEL)",
  'ACTIVITY_RESET': r"(?P<self>[A-Z][a-z]+) (?i:\+RESET)",
  'ACTIVITY_BUY_GUILD': r"^You say to your guild, '(?i:\+GRATS)\s+(?P<name>[A-Za-z]+)\s+(?P<dkp>\d+)\s+(?P<item>.+)'",
  'ACTIVITY_BUY_SELF': r"(?P<self>[A-Z][a-z]+) (?i:\+GRATS)\s+(?P<name>[A-Za-z]+)\s+(?P<dkp>\d+)\s+(?P<item>.+)",
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

def gen_messages(file_gen):
  for line in file_gen:
    log_match = re.match(PATTERNS['DEFAULT'], line)
    if log_match is None:
      continue

    message = log_match.group("message")
    if message is None:
      continue

    yield message

def is_site_integration_enabled():
  if os.path.exists('cookies.pkl'):
    try:
      events = get_events()
      if len(events) != 0:
        return True
    except Exception as err:
      return False
  return False

def gen_raid_activity(file_gen):
  reading_activity = False
  reading_slash_who = False
  for message in gen_messages(file_gen):
    system_test_match = re.match(PATTERNS['ACTIVITY_SYSTEM_TEST'], message)
    if system_test_match is not None:
      name = system_test_match.group("self")
      logger.info('[SYSTEM CHECK] {}'.format(name))
      logger.info('[SYSTEM CHECK] Site integration {}'.format(is_site_integration_enabled()))
      logger.info('[SYSTEM CHECK] Discord integration {}'.format(get_webhook_url()))
      logger.info('[SYSTEM CHECK] Reading activity {}'.format(reading_activity))
      logger.info('[SYSTEM CHECK] Reading /who {}'.format(reading_slash_who))
      yield ('SYSTEM_CHECK', None)
      continue

    reset_match = re.match(PATTERNS['ACTIVITY_RESET'], message)
    if reset_match is not None:
      logger.info('Resetting all state tracking')
      reading_activity = False
      reading_slash_who = False
      yield ('RESET', None)
      continue

    cancel_match = re.match(PATTERNS['ACTIVITY_CANCEL'], message)
    if cancel_match is not None:
      if reading_activity:
        logger.info('[CANCEL] Canceling ongoing read operations')
        reading_activity = False
        reading_slash_who = False
        yield ('CANCEL', None)
      else:
        logger.info('[CANCEL] Nothing to cancel')
      continue

    buy_match_guild = re.match(PATTERNS['ACTIVITY_BUY_GUILD'], message)
    if buy_match_guild is not None:
      name, dkp, item = buy_match_guild.group("name", "dkp", "item")
      yield ('BUY', { 'name': name.capitalize(), 'dkp': int(dkp), 'item': item })
      continue

    buy_match_self = re.match(PATTERNS['ACTIVITY_BUY_SELF'], message)
    if buy_match_self is not None:
      name, dkp, item = buy_match_self.group("name", "dkp", "item")
      yield ('BUY', { 'name': name.capitalize(), 'dkp': int(dkp), 'item': item })
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

    pilot_match_self = re.match(PATTERNS['ACTIVITY_PILOT_SELF'], message)
    if pilot_match_self is not None:
      pilot, bot = pilot_match_self.group("pilot", "bot")
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

    if not reading_activity:
      start_match = re.match(PATTERNS["ACTIVITY_START"], message)
      if start_match is not None:
        reading_activity = True
        category, name, dkp = start_match.group("category", "name", "dkp")
        sid = get_sid()
        yield ('START', { 'category': category.upper(), 'name': '{} ({})'.format(name, sid), 'dkp': int(dkp) if dkp is not None else 1, 'sid': sid, })
      continue

    if message.startswith("There are"):
      logger.info('Saw "There are"; stop reading /who')
      reading_activity = False
      reading_slash_who = False
      yield ('END', None)
      continue
    elif message.startswith("Players on EverQuest:"):
      logger.info('Saw "Players on EverQuest"; reading /who')
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

    absent_match = re.match(PATTERNS['ACTIVITY_ABSENT'], message)
    if absent_match is not None:
      name = absent_match.group("name")
      yield ('ABSENT', { 'name': name.capitalize() })
      continue

    absent_match_alternate = re.match(PATTERNS['ACTIVITY_ABSENT_ALTERNATE'], message)
    if absent_match_alternate is not None:
      name = absent_match_alternate.group("name")
      yield ('ABSENT', { 'name': name.capitalize() })
      continue

    absent_match_guild = re.match(PATTERNS['ACTIVITY_ABSENT_GUILD'], message)
    if absent_match_guild is not None:
      name = absent_match_guild.group("name")
      yield ('ABSENT', { 'name': name.capitalize() })
      continue

def get_raid_attendance(pilots: Dict[str, str], guests: Set[str], guilds: Set[str], absentees: Set[str], attendance) -> None:
  pilots = pilots or {}
  guests = guests or set()
  guilds = guilds or set()
  absentees = absentees or set()
  attendance = attendance or {}
  # Filter out entries for players not in guilds list
  raid_attendance = {
    player: attendance for player, attendance in attendance.items() if attendance.get('guild') in guilds
  }

  # Keep entries for guests in guests list
  for guest in guests:
    if guest not in raid_attendance and guest in attendance:
      raid_attendance[guest] = attendance.get(guest, { 'name': guest, 'level': None, 'class': None, 'guild': None })

  # Remove bot from attendance entries for pilots
  for bot, pilot in pilots.items():
    if bot in raid_attendance:
      raid_attendance.pop(bot)

    # If the bot isn't present, we're not including it in attendance
    if bot in attendance:
      # We build them like an anon user because they naturally should not be online
      raid_attendance[pilot] = { 'name': pilot, 'level': None, 'class': None, 'guild': None }
  
  for absentee in absentees:
    name = absentee if absentee not in pilots else pilots.get(absentee)
    raid_attendance[name] = { 'name': name, 'level': None, 'class': None, 'guild': None }

  return raid_attendance

def gen_raid_outcomes(file_gen):
  event = None
  guilds: Set[str] = {'LINEAGE'} # Maybe set via CLI as the host guild
  absentees: Optional[Set[str]] = None
  attendance = None
  pilots: Dict[str, str] = {}
  guests: Set[str] = set()
  for (kind, message) in gen_raid_activity(file_gen):
    logger.info('{}, {}'.format(kind, message))
    if kind == 'START':
      event = message
      absentees = set()
      attendance = {}
    elif kind == 'END':
      raid_attendance = get_raid_attendance(pilots, guests, guilds, absentees, attendance)
      debug = debug_obj(pilots, guests, guilds, absentees, attendance, raid_attendance)
      yield ('ATTENDANCE', (event, raid_attendance, debug))
      event = None
      absentees = None
      attendance = None
    elif kind == 'BUY':
      yield ('PURCHASE', message)
    elif kind == 'ATTENDEE':
      name = message.get('name')
      attendance[name] = message
    elif kind == 'PILOT':
      pilots[message.get('bot')] = message.get('pilot')
    elif kind == 'GUEST':
      guests.add(message.get('name'))
    elif kind == 'GUILD':
      guilds.add(message.get('name'))
    elif kind == 'ABSENT':
      absentees.add(message.get('name'))
    elif kind == 'SYSTEM_CHECK':
      logger.info('[SYSTEM CHECK] Event {}'.format(event))
      raid_attendance = get_raid_attendance(pilots, guests, guilds, absentees, attendance)
      debug = debug_obj(pilots, guests, guilds, absentees, attendance, raid_attendance)
      logger.info('[SYSTEM CHECK] State {}'.format(debug))
      logger.info('[SYSTEM CHECK] State \n{}'.format(debug_str(**debug)))
    elif kind == 'CANCEL':
      logger.info('[CANCEL] Clearing tick state')
      event = None
      absentees = None
      attendance = None
    elif kind == 'RESET':
      logger.info('[RESET] Clearing all state')
      event = None
      guilds = {'LINEAGE'}
      pilots = {}
      guests = set()
      absentees = None
      attendance = None

def monitor():
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
  if file_path is None or file_path == '':
    logger.info('No file selected, closing.')
    sys.exit()

  logger.info('Monitoring {}'.format(file_path))

  file_gen = gen_tail(file_path)
  purchases = []
  last_event = None
  # Set to none initially, meaning we'll need / end up creating one. This will
  # remain fixed to a message on a per-event basis, being reset each time a new
  # event kicks off.
  purchase_message_id = None
  for (kind, message) in gen_raid_outcomes(file_gen):
    if kind == 'ATTENDANCE':
      purchase_message_id = None
      purchases = []
      event, attendance, debug = message
      last_event = event
      for name, attendee in attendance.items():
        logger.info('Confirmed {}, {}'.format(name, attendee))
      try:
        upload_attendance(event, attendance, debug)
      except Exception as err:
        logger.error('Problem uploading attendance, check log for issues and consider trying again, {}'.format(err))
    elif kind == 'PURCHASE':
      item = message
      purchase_message_id, purchase = upload_purchase(purchases, item, last_event, purchase_message_id)
      purchases.append(purchase)

if __name__ == "__main__":
  monitor()