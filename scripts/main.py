import sys
import os
import inquirer
import pyfiglet
from time import sleep
from sys import exit
from monitor import monitor
from upload_guest_log import upload_raid_file
from guest_monitor import guest_monitor
from peek_guest_log import view_raid_file
from readme import readme

def print_title():
  result = pyfiglet.figlet_format("DKP TOOLS", font = "slant")

  # Append author attribution to the correct line of output
  lines = result.splitlines()
  lines[-2] += ' by Lineage'

  # Join the lines back together
  joined = '\n'.join(lines)
  print(joined)

def main():
  choices=[
    "Monitor logs (admin)",
    "Upload raid file (admin)",
    "Monitor logs (guest)",
    "View contents of raid file",
    "README",
    "Quit",
  ]

  while True:
    os.system('clear')
    print_title()

    questions = [
      inquirer.List(
        'choice',
        message="Please choose one of the options below:",
        choices=choices,
        carousel=True
      )
    ]

    answers = inquirer.prompt(questions)
    choice = answers['choice']

    if choice == choices[5]:
      sys.exit()

    try:
      if choice == choices[0]:
        os.system('clear')
        monitor()
      elif choice == choices[1]:
        os.system('clear')
        upload_raid_file()
        input("Press Enter to return to menu.")
      elif choice == choices[2]:
        os.system('clear')
        guest_monitor()
      elif choice == choices[3]:
        os.system('clear')
        view_raid_file()
        input("Press Enter to return to menu.")
      elif choice == choices[4]:
        readme()
      else:
        print("Invalid choice. Please choose a valid option.")
    except (Exception, SystemExit, KeyboardInterrupt) as err:
      input("Press Enter to return to menu.")

if __name__ == "__main__":
  main()