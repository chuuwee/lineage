import os
import random
import pickle
import secrets
import string
import pytz
from datetime import datetime
from version import VERSION
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

# Generate five-character random identifier for events
def get_sid():
  # Define the character set
  characters = string.ascii_lowercase + string.digits

  # Generate a random five-character string
  return ''.join(secrets.choice(characters) for _ in range(5))

def get_webhook_url():
  if os.path.exists('webhookurl.txt'):
    with open('webhookurl.txt', 'rb') as f:
      return f.read().strip().decode()
  if os.path.exists('webhook.url'):
    with open('webhook.url', 'rb') as f:
      return f.read().strip().decode()
  return None

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

def discord_format_absentee(absentee, pilot):
  if pilot is not None:
    return '{} ({})'.format(pilot, absentee)
  return '{}'.format(absentee)

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

def get_purchase_from_item(item):
  # Set the timezone to Central Standard Time
  central = pytz.timezone('US/Central')

  color = generate_light_color()

  # Get the current time in Central Standard Time
  now = datetime.now(central)

  # Format the current time as a string in the desired format
  date_str = "{}/{}/{}".format(now.month, now.day, now.year)

  return {
    **item,
    'color': color,
    'date': now,
    'date_str': date_str,
  }

def report_purchase_to_discord_guest(purchases, filename, raw_pickle, last_event, message_id):
  event_name = last_event['name'] if last_event else None
  webhook_url = get_webhook_url()
  if webhook_url is None:
    logger.info('No webhook.url file found. See README.md to send Discord reports.')
    return

  purchase_message = "**🚨 GUEST CAPTURE -- UNPOSTED 🚨**"
  if message_id is not None:
    wh = DiscordWebhook(url=webhook_url, id=message_id)
  else:
    # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
    wh = DiscordWebhook(url=webhook_url, content=purchase_message)

  def setup_webhook(webhook):
    tally_str = '{} Purchase{}'.format(len(purchases), 's' if len(purchases) > 1 else '')
    embed = DiscordEmbed(
      title="{}{}".format(event_name + ' - ' if event_name else '', tally_str),
      description='\n\n'.join(['<t:{}:t>\n**{}**\n{} **{} DKP**'.format(round(purchase['date'].timestamp()), purchase['item'], purchase['name'], purchase['dkp']) for purchase in purchases]),
      color=purchases[0]['color'] # We use the first one for simplicity / to keep it constant
    )
    # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
    embed.add_embed_field(
      name=" ",
      value="Generated by [DKP script v{}](https://github.com/chuuwee/lineage).".format(VERSION),
      inline=False
    )
    webhook.add_embed(embed)
    # swapping to description with newlines and add the footer and change title
    # / guest capture webhook-level message

  setup_webhook(wh)
  if message_id:
    wh.edit()
  else:
    wh.execute()

  logger.info('Posted Discord message with id: {}'.format(wh.id))
  # serialize the cookies to a file
  with open('{}.grats'.format(filename), 'wb') as f:
    logger.info('Writing file, {}'.format('{}.raid'.format(filename)))
    # Store bytes to send to Discord webhook
    file_for_discord = pickle.dumps({
      **raw_pickle,
      'message_id': wh.id,
    })
    # Write to local file
    pickle.dump({
      **raw_pickle,
      'message_id': wh.id,
    }, f)

    # Create webhook
    wh_with_file = DiscordWebhook(url=webhook_url, id=wh.id, content=purchase_message)
    setup_webhook(wh_with_file)
    wh_with_file.add_file(file=file_for_discord, filename='{}.grats'.format(filename))
    wh_with_file.edit()
    logger.info('Updated and added file to discord message with id: {}'.format(wh.id))
  return wh.id

def report_purchase_to_discord(purchases, last_event, message_id):
  event_name = last_event['name'] if last_event else None
  webhook_url = get_webhook_url()
  if webhook_url is None:
    logger.info('No webhook.url file found. See README.md to send Discord reports.')
    return

  if message_id is not None:
    webhook = DiscordWebhook(url=webhook_url, id=message_id)
  else:
    # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
    webhook = DiscordWebhook(url=webhook_url)

  tally_str = '{} Purchase{}'.format(len(purchases), 's' if len(purchases) > 1 else '')
  embed = DiscordEmbed(
    title="{}{}".format(event_name + ' - ' if event_name else '', tally_str),
    description='\n\n'.join(['<t:{}:t>\n**{}**\n{} **{} DKP**'.format(round(purchase['date'].timestamp()), purchase['item'], purchase['name'], purchase['dkp']) for purchase in purchases]),
    color=purchases[0]['color'] # We use the first one for simplicity / to keep it constant
  )
  # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
  embed.add_embed_field(
    name=" ",
    value="Generated by [DKP script v{}](https://github.com/chuuwee/lineage).".format(VERSION),
    inline=False
  )
  webhook.add_embed(embed)
  if message_id:
    webhook.edit()
  else:
    webhook.execute()
  return webhook.id

def report_to_discord(name, date, dkp, id, debug):
  webhook_url = get_webhook_url()
  if webhook_url is None:
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
  embed.add_embed_field(name='Pilots', value='```\n{}\n```'.format('\n'.join(pilot_list)) if len(pilot_list) else '```\nNONE\n```', inline=True)
  embed.add_embed_field(name='Absentees', value='```\n{}\n```'.format('\n'.join(absentee_list)) if len(absentee_list) else '```\nNONE\n```', inline=True)

  if len(guest_list) != 0:
    embed.add_embed_field(name='Guests', value='```\n{}\n```'.format('\n'.join(guest_list)), inline=False)

  # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
  embed.add_embed_field(
    name=" ",
    value="Generated by [DKP script v{}](https://github.com/chuuwee/lineage).".format(VERSION),
    inline=False
  )

  # Create webhook
  webhook = DiscordWebhook(url=webhook_url)

  # Add embed to webhook
  webhook.add_embed(embed)

  # Send the webhook
  webhook.execute()

def report_to_discord_guest(name, date, dkp, filename, raw_pickle, debug):
  logger.info('Attempting to report to Discord, {}, {}, {}, {}'.format(name, date, dkp, filename))
  webhook_url = get_webhook_url()
  if webhook_url is None:
    logger.info('No webhook.url file found - CANCELING REPORT. See README.md to send Discord reports.')
    return
  
  # Create webhook
  wh = DiscordWebhook(url=webhook_url)

  def setup_webhook(webhook):
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
      description='**Captured <t:{}>**\n**{}**\n**{} DKP**'.format(round(date.timestamp()), guilds, dkp, id),
      color=generate_light_color()
    )

    # Add the participant lists as fields to the embed message
    embed.add_embed_field(name='Credited @ Raid', value='```\n{}\n```'.format('\n'.join(raid_list)), inline=False)
    embed.add_embed_field(name='/who', value='```\n{}\n```'.format('\n'.join(who_list)), inline=True)
    embed.add_embed_field(name='Pilots', value='```\n{}\n```'.format('\n'.join(pilot_list)) if len(pilot_list) else '```\nNONE\n```', inline=True)
    embed.add_embed_field(name='Absentees', value='```\n{}\n```'.format('\n'.join(absentee_list)) if len(absentee_list) else '```\nNONE\n```', inline=True)

    if len(guest_list) != 0:
      embed.add_embed_field(name='Guests', value='```\n{}\n```'.format('\n'.join(guest_list)), inline=False)

    # TODO(ISSUE-12): Dynamically update version so it doesn't mistakenly get stale.
    embed.add_embed_field(
      name=" ",
      value="Generated by [DKP script v{}](https://github.com/chuuwee/lineage).".format(VERSION),
      inline=False
    )

    # Add embed to webhook
    webhook.add_embed(embed)

  setup_webhook(wh)
  # Send the webhook
  wh.execute()

  logger.info('Posted Discord message with id: {}'.format(wh.id))
  # serialize the cookies to a file
  with open('{}.raid'.format(filename), 'wb') as f:
    logger.info('Writing file, {}'.format('{}.raid'.format(filename)))
    # Store bytes to send to Discord webhook
    file_for_discord = pickle.dumps({
      **raw_pickle,
      'message_id': wh.id,
    })
    # Write to local file
    pickle.dump({
      **raw_pickle,
      'message_id': wh.id,
    }, f)

    # Create webhook
    wh_with_file = DiscordWebhook(url=webhook_url, id=wh.id, content="**🚨 GUEST CAPTURE -- UNPOSTED 🚨**")
    setup_webhook(wh_with_file)
    wh_with_file.add_file(file=file_for_discord, filename='{}.raid'.format(filename))
    wh_with_file.edit()
    logger.info('Updated and added file to discord message with id: {}'.format(wh.id))