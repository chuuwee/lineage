# DKP Tools

Tools to support raid / guild leads by and for Lineage. Longer term plans for
portability to other sites or guilds.

## Instructions

  * Monitor logs (admin)
  * Upload raid file (admin)
  * Monitor logs (guest)
  * View contents of raid file

### Monitor logs (admin)

Site admins must log in with their credentials, select a logfile to monitor, and
utilize a series of [in game commands](#in-game-commands) to trigger event
collection or attendance corrections. Requires [webhook file](#discord) to
submit to Discord.

### Upload raid file (admin)

Site admins must log in with their credentials and select a `.raid` file to
upload. Requires [webhook file](#discord) to submit to Discord.

### Monitor logs (guest)

If you are not an admin but would like to help out, this tool can be utilized to
capture `.raid` files for later upload by an admin. If you're interested, I'd
suggest contacting a lead on Discord for more info on the [webhook
file](#discord).

Much like the admin monitor but without login, you select a logfile to monitor,
and utilize a series of [in game commands](#in-game-commands) to trigger event
collection or attendance corrections.

### View contents of raid file

Run and select a `.raid` file to see a summary of the contents.

### Discord

Reporting to Discord requires the presence of `webhookurl.txt` (though
`webhook.url` is still supported) in the same directory as `dkp-tools.exe`. This
contains a private webhook address and can be requested from a lead over
Discord.

## In game commands

With the monitor running on your EverQuest log (and logging enabled in game),
you begin the process of capturing attendance by writing one of the trigger
statements into guild chat.

### +TARGET, +EVENT, +LOCALE
* `/guild +TARGET Cazic-Thule`
* `/guild +EVENT Farming Quillmane`
* `/guild +LOCALE Plane of Fear`

You can set a custom DKP value (default is 1):

* `/guild +TARGET 3 Cazic-Thule`

The string after the type and optional DKP is open-ended, so you can consider
explaining context in it, too:

* `/guild +TARGET 2 Quillmane Hour 1`
* `/guild +TARGET 2 Quillmane Hour 2`

There are a handful of commands users can run at any point during collection to influence how we record during events:

### +PILOT
Piloting a bot?
* `/tell Yourname +PILOT Pilotsrealcharname`
* `/gu +PILOT Pilotsrealcharname`

If (AND ONLY IF) you are the raid leader, and you are driving a bot, you can use emotes to remove the bot from attendance log and put yourself in its place:
* `/em +PILOT Pilotsrealcharname`

### +GUILD
Adding a guest guild:
* `/guild +GUILD Nova`

### +GUEST
Adding a guest player requires they send you a tell:
* `/tell Yourname +GUEST`

### +ABSENT
Some commands require the tick being captured to operate. In particular,
recording absence (as we don't want to collect absence in a persistent way, but
only when someone isn't in zone for tick due to legitimate reasons). This will
record the correct usage *even if they are driving a bot*, so long as they've
already reported their bot driving with a `+PILOT` command prior.
* `/tell Yourname +ABSENT`
* `/gu +ABSENT`

LASTLY, run a final `/who` command to kick off capturing of players in zone.
This will resolve attendance alongside the corrections and upload it to the
website.

### +CANCEL
If you'd like to cancel an event mid-collection to restart it:
* `/em +CANCEL`

### +RESET
If you want to clear out the list of current guilds, guests, or bot pilots:
* `/em +RESET`

## Debugging

### +TEST
IF you'd like to check the current state of data collection, run:
* `/em +TEST`

`debug.log` is written to the root directory and contains detailed tracking of
script execution.