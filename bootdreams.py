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
  
  

