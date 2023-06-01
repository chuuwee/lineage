import sys
import os
import inquirer
from time import sleep
from sys import exit
from monitor import monitor
from upload_guest_log import upload_raid_file
from guest_monitor import guest_monitor
from peek_guest_log import view_raid_file
from readme import readme
from rich.console import Console

console = Console()

def print_title():
  print('')
  print('    ____  __ __ ____     ______            __    ')
  print('   / __ \/ //_// __ \   /_  __/___  ____  / /____')
  print('  / / / / ,<  / /_/ /    / / / __ \/ __ \/ / ___/')
  print(' / /_/ / /| |/ ____/    / / / /_/ / /_/ / (__  ) ')
  print('/_____/_/ |_/_/        /_/  \____/\____/_/____/  by Lineage')
  print('')

def main():
  choices=[
    "Monitor logs (admin)",
    "Upload raid file (admin)",
    "Monitor logs (guest)",
    "View contents of raid file",
    "Quit",
  ]

  while True:
    console.clear()
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

    if choice == choices[4]:
      sys.exit()

    if choice == choices[0]:
      console.clear()
      monitor()
      sys.exit()
    elif choice == choices[1]:
      console.clear()
      upload_raid_file()
      sys.exit()
    elif choice == choices[2]:
      console.clear()
      guest_monitor()
      sys.exit()
    elif choice == choices[3]:
      console.clear()
      view_raid_file()
      sys.exit()
    else:
      print("Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
  main()