import os
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from logger import get_logger

class_dict = {
    "Bard": ["Minstrel", "Troubadour", "Virtuoso"],
    "Beastlord": ["Primalist", "Animist", "Savage Lord"],
    "Berserker": ["Brawler", "Vehement", "Rager"],
    "Cleric": ["Vicar", "Templar", "High Priest"],
    "Druid": ["Wanderer", "Preserver", "Hierophant"],
    "Enchanter": ["Illusionist", "Beguiler", "Phantasmist"],
    "Magician": ["Elementalist", "Conjurer", "Arch Mage"],
    "Monk": ["Disciple", "Master", "Grandmaster"],
    "Necromancer": ["Heretic", "Defiler", "Warlock"],
    "Paladin": ["Cavalier", "Knight", "Crusader"],
    "Ranger": ["Pathfinder", "Outrider", "Warder"],
    "Rogue": ["Rake", "Blackguard", "Assassin"],
    "Shadow Knight": ["Reaver", "Revenant", "Grave Lord"],
    "Shaman": ["Mystic", "Luminary", "Oracle"],
    "Warrior": ["Champion", "Myrmidon", "Warlord"],
    "Wizard": ["Channeler", "Evoker", "Sorcerer"]
}

logger = get_logger('utils')

class_name_by_alias = {}
for true_class, aliases in class_dict.items():
  for alias in aliases:
    class_name_by_alias[alias] = true_class
  class_name_by_alias[true_class] = true_class

def generate_light_color():
  # Define the minimum value for each RGB component (can be adjusted)
  min_value = 100

  # Generate random RGB values within the allowed range
  r = random.randint(min_value, 255)
  g = random.randint(min_value, 255)
  b = random.randint(min_value, 255)

  # Combine the RGB values into a single hexadecimal number
  color = (r << 16) + (g << 8) + b

  return hex(color)

def format_absentee(absentee, pilot):
  if pilot is not None:
    return '  {}/{}'.format(pilot, absentee)
  return '  {}'.format(absentee)

def discord_format_absentee(absentee):
  name, pilot = absentee.get('name'), absentee.get('pilot')
  if pilot is None:
    return name
  return '{} ({})'.format(pilot, name) 

def debug_obj(pilots, guests, guilds, absentees, attendance, raid_attendance):
  return {
    'pilots': pilots,
    'guests': guests,
    'guilds': guilds,
    'absentees': absentees,
    'attendance': attendance,
    'raid_attendance': raid_attendance,
  }

def debug_str(pilots, guests, guilds, absentees, attendance, raid_attendance):
  pilots = pilots or {}
  guests = guests or set()
  guilds = guilds or set()
  absentees = absentees or set()
  attendance = attendance or {}
  raid_attendance = raid_attendance or {}
  return 'RAID\n{}\nPILOT/BOTS\n{}\nGUESTS\n{}\nABSENTEES/BOTS\n{}\nGUILDS\n{}\nWHO\n{}\n'.format(
    '\n'.join(sorted(['  {}'.format(name) for name, attendee in raid_attendance.items()])),
    '\n'.join(sorted(['  {}/{}'.format(pilot, bot) for bot, pilot in pilots.items()])),
    '\n'.join(sorted(['  {}'.format(guest) for guest in guests])),
    '\n'.join(sorted([format_absentee(absentee, pilots.get(absentee)) for absentee in absentees])),
    '\n'.join(sorted(['  {}'.format(guild) for guild in guilds])),
    '\n'.join(sorted(['  {}'.format(name) for name, attendee in attendance.items()])),
  )

def report_to_discord(name, date, dkp, id, debug):
  if os.path.exists('webhook.url'):
    with open('webhook.url', 'rb') as f:
      webhook_url = f.read().strip()
  else:
    logger.info('No webhook.url file found. See README.md to send Discord reports.')
    return

  pilots = debug.get('pilots')
  guests = debug.get('guests')
  guilds = debug.get('guilds')
  absentees = debug.get('absentees')
  attendance = debug.get('attendance')
  raid_attendance = debug.get('raid_attendance')

  raid_list = sorted([name for name, attendee in raid_attendance.items()])
  pilot_list = sorted(['{} ({})'.format(pilot, bot) for bot, pilot in pilots.items()])
  absentee_list = sorted([discord_format_absentee(absentee, pilots.get(absentee)) for absentee in absentees])
  who_list = sorted([name for name, attendee in attendance.items()])
  guest_list = sorted(guests)
  guilds = ', '.join([guild.title() for guild in guilds])

  # Define the embed message
  embed = DiscordEmbed(
    title=name,
    description='**Captured <t:{}>**\n**{}**\n**{} DKP**\n[View details](http://lineageeq.dkpsystem.com/eventdetails.php?id={})'.format(round(date.timestamp()), guilds, dkp, id),
    color=generate_light_color()
  )

  # Add the participant lists as fields to the embed message
  embed.add_embed_field(name='Credited @ Raid', value='```\n{}\n```'.format('\n'.join(raid_list)), inline=False)
  embed.add_embed_field(name='/who', value='```\n{}\n```'.format('\n'.join(who_list)), inline=True)
  embed.add_embed_field(name='Pilots', value='```\n{}\n```'.format('\n'.join(pilot_list)), inline=True)
  embed.add_embed_field(name='Absentees', value='```\n{}\n```'.format('\n'.join(absentee_list)), inline=True)

  if len(guest_list) != 0:
    embed.add_embed_field(name='Guests', value='```\n{}\n```'.format('\n'.join(guest_list)), inline=False)

  # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
  embed.add_embed_field(
    name=" ",
    value="Generated by [DKP script v0.1.0](https://github.com/chuuwee/lineage).",
    inline=False
  )

  # Create webhook
  webhook = DiscordWebhook(url=webhook_url)

  # Add embed to webhook
  webhook.add_embed(embed)

  # Send the webhook
  webhook.execute()

