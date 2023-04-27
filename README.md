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

* `/guild ELFSIM TARGET Cazic-Thule`
* `/guild ELFSIM EVENT Farming Quillmane`
* `/guild ELFSIM LOCALE Plane of Fear`

You also might consider capturing the timing with it, or the DKP if you'd like it to be a value other than 1.

* `/guild ELFSIM TARGET 3 Cazic-Thule`
* `/guild ELFSIM EVENT Farming Quillmane Hour 3`
* `/guild ELFSIM LOCALE 2 Plane of Fear Hour 2`

Once you've run ONE of the above commands, there are a handful of additional correction commands.

Adding a guest guild:
* `/guild ELFSIM +GUILD Nova`

Adding a guest player requires they send you a tell:
* `/tell Yourname ELFSIM GUEST`

Specifying bot usage similarly requires sending a tell:
* `/tell Yourname ELFSIM PILOT Pilotsrealcharname`

LASTLY, run a final `/who` command to kick off capturing of players in zone.
This will resolve attendance alongside the corrections and upload it to the
website.