import logging
import os
import sys

def get_logger(log_name):
  # TODO(ISSUE-11): We should create an entry point where this can be centralized, but
  # it's duplicated in the logger for now.
  if getattr(sys, 'frozen', False):
    # we are running in a bundle
    executable_path = sys.executable
    executable_dir = os.path.dirname(executable_path)
    os.chdir(executable_dir)

  logger = logging.getLogger(log_name)
  logger.setLevel(logging.INFO)

  # Create a file handler for the logger
  handler = logging.FileHandler('debug.log')

  # Create a stream handler for the logger
  stream_handler = logging.StreamHandler()

  # Create a formatter for the log messages
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%m/%d/%Y %H:%M:%S%z')
  handler.setFormatter(formatter)
  stream_handler.setFormatter(formatter)

  # Add the handler to the logger
  logger.addHandler(handler)
  logger.addHandler(stream_handler)

  return logger