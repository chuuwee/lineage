# Lineage

Short set of applications intended to support raid / guild leads in populating
DKP tracking website.

## Instructions

There are three applications available in the tool kit:

* `dkp-monitor.exe`
  * This is for raid leads / site admins who can submit DKP logs freely. It will
  request a login and password for the site, followed by your characters
  logfile.
* `dkp-monitor-guest.exe`
  * This is for raiders who would like to assist in running a raid, and can run
  what amounts to an offline version of the above scripts. It will ask for your
  characters logfile, and generate files with extension *.raid as you capture
  raid attendance. Hand these to a raid lead for upload.
* `dkp-upload.exe`
  * Parses *.raid files of captured raids. Will ask for your login (unless
  you're logged in) and the location of the relevant *.raid file.
* `dkp-peek.exe`
  * Prints summary of a *.raid file. Will prompt for location of a .raid file
  and print contents. Useful for admins to validate logs before upload.

All three applications will output state information about what they're
capturing as they run.

Consider keeping your log around in the event you need or want to corroborate
any of the application's decisions.

### In game commands

With the monitor running on your EverQuest log (and logging enabled in game),
you begin the process of capturing attendance by writing one of the trigger
statements into guild chat.

#### +TARGET, +EVENT, +LOCALE
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

#### +PILOT
Piloting a bot?
* `/tell Yourname +PILOT Pilotsrealcharname`
* `/gu +PILOT Pilotsrealcharname`

If (AND ONLY IF) you are the raid leader, and you are driving a bot, you can use emotes to remove the bot from attendance log and put yourself in its place:
* `/em +PILOT Pilotsrealcharname`

#### +GUILD
Adding a guest guild:
* `/guild +GUILD Nova`

#### +GUEST
Adding a guest player requires they send you a tell:
* `/tell Yourname +GUEST`

#### +ABSENT
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

#### +CANCEL
If you'd like to cancel an event mid-collection to restart it:
* `/em +CANCEL`

#### +RESET
If you want to clear out the list of current guilds, guests, or bot pilots:
* `/em +RESET`

### Debugging

#### +TEST
IF you'd like to check the current state of data collection, run:
* `/em +TEST`

`debug.log` is written to the root directory and contains detailed tracking of
script execution.