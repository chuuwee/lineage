# Lineage

Short set of scripts intended to support raid / guild leads in populating DKP
tracking website.

## Instructions

### Running script
* Install Python 3.10
* Run `pip install -r requirements.txt` to get dependencies.
* Run `python scripts/login.py`
* Run `python scripts/monitor.py`

### In game commands

With the monitor running on your EverQuest log (and logging enabled in game),
you begin the process of capturing attendance by writing one of the trigger
statements into guild chat.

* `/guild +TARGET Cazic-Thule`
* `/guild +EVENT Farming Quillmane`
* `/guild +LOCALE Plane of Fear`

You can set a custom DKP value (default is 1):

* `/guild +TARGET 3 Cazic-Thule`

The string after the type and optional DKP is open-ended, so you can consider
explaining context in it, too:

* `/guild +TARGET 2 Quillmane Hour 1`
* `/guild +TARGET 2 Quillmane Hour 2`

Once you've run ONE of the above commands, there are a handful of additional
correction commands.

Adding a guest guild:
* `/guild +GUILD Nova`

Adding a guest player requires they send you a tell:
* `/tell Yourname +GUEST`

Specifying bot usage similarly requires them sending a tell or notifying the
guild:
* `/tell Yourname +PILOT Pilotsrealcharname`
* `/gu +PILOT Pilotsrealcharname`

If they are not present in zone, they can similarly send a tell or notify the
guild:
* `/tell Yourname +ABSENT`
* `/gu +ABSENT`

And if they are absent while driving a bot:
* `/tell Yourname +ABSENT Pilotsrealcharname`
* `/gu +ABSENT Pilotsrealcharname`

LASTLY, run a final `/who` command to kick off capturing of players in zone.
This will resolve attendance alongside the corrections and upload it to the
website.

### Debugging

`debug.log` is written to the root directory and contains detailed tracking of
script execution.