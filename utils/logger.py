import logging
import os

# Set up the log file path
log_file = "app.log"

# Create a logger
logger = logging.getLogger('app_logger')
logger.setLevel(logging.DEBUG) 

# Create a file handler to log to the file
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)  
# Create a log formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Add a stream handler to also log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) 
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
