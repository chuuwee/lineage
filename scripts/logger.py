import logging

def get_logger(log_name):
  logger = logging.getLogger(log_name)
  logger.setLevel(logging.INFO)

  # Create a file handler for the logger
  handler = logging.FileHandler('debug.log')

  # Create a formatter for the log messages
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%m/%d/%Y %H:%M:%S%z')
  handler.setFormatter(formatter)

  # Add the handler to the logger
  logger.addHandler(handler)

  return logger