#!/usr/bin/python2
# Bootdreams python
# Written by Joe Balough (sl)
# Licensed under the GPL
version = 0.1
print("Bootdreams Python Version " + str(version))


# Import relevant modules
import sys
# For running commands and getting their output to stdout
import subprocess
# For string.lower
import string
# To determine if file exits
import os
# Regular expressions
import re


# Help printing function
def print_help():
  print("Usage: " + sys.argv[0] + " Image_File.cdi [Write Speed] [/path/to/burner]")
  print("Acceptable image formats are Discjuggler (CDI), ISO, and BIN/CUE.")
  print("Write speed and burner path are optional. If omitted, the slowest speed and the first burner are used.")



# The file to process
try:
  input_image = sys.argv[1]
except IndexError:
  print("ERROR: No File Specified.")
  print_help()
  sys.exit(1)

# See if user was trying to get help
if string.lower(input_image) == "help" or string.lower(input_image) == "--help" or string.lower(input_image) == "-h":
  print_help()
  sys.exit(1)

# Make sure file exists
if not os.path.isfile(input_image):
  print("ERROR: File not found.")
  print_help()
  sys.exit(1)

# Convert extension to lower case to properly handle it
input_ext = string.lower(input_image[-3:])




# CDI FILE HANDLING
if input_ext == "cdi":
  
  # Get information about this cdi file
  cdi_info = subprocess.check_output(["cdirip", input_image, "-info"])
  
  # Make a list containing lists of track types for each session.
  # First dimension is Session number, second is Track number
  session_data = []
  
  # Split the cdi_info string by the Session i has d track(s) string. Discard the first because it offers no data
  for i in re.split('Session \d+ has \d+ track\(s\)', cdi_info)[1:]:
    # Get all the track types in a list and append it to the list of session data
    session_data.append(re.findall('Type: (\S*)', i))
  
  # Check for situations to warn the user about:
  # More than 2 sessions:
  if len(session_data) > 2:
    print("Warning: CDI image has more than 2 sessions. Continuing anyway though this is untested.")
  
  # Unsupported session type
  for s in session_data:
    for t in s:
      if not t in ["Mode1/2048", "Mode2/2336", "Audio/2352"]:
        print("ERROR: Unsupported session type " + t + ". Only Mode1/2048, Mode2/2336, and Audio/2352 are supported.")
        exit(1)
  
  # data/data image with CDDA
  if session_data[0] == ["Mode2/2336", "Audio/2352"]:
    print("Warning: CDRecord cannot properly burn a data/data DiscJuggler image with CDDA.")
    print("         You can continuing anyway though it may be a coaster if there is very little space left in the image.")
    to_continue = string.lower(raw_input("         Would you like to continue (Y/n)? "))
    if to_continue != "" and to_continue[0] == 'n':
      exit(1)
      
  