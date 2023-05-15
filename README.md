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

If (AND ONLY IF YOU) you are the raid leader, and you are driving a bot, you can use emotes to remove the bot from attendance log and put yourself in its place:
* `/em +PILOT Pilotsrealcharname`

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