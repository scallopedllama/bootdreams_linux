#!/usr/bin/python2

#     Bootdreams python
#     Written by Joe Balough (sallopedllama at gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

version = 0.3
print ("Bootdreams dot py   Version " + str(version))
do_burn = True

# Import relevant modules
import sys
# For running commands and getting their output to stdout
import subprocess
# For string.lower
import string
# To determine if file exits
import os
# For rmtree
import shutil
# Regular expressions
import re


# Query wodim for burners
# Oddly enough, wodim returns an error code if you have a burner but returns 0 if you don't.
def query_burners():
  try:
    output = subprocess.Popen(['wodim', '--devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    return re.findall("dev='(\S*)'", output)
  except subprocess.CalledProcessError, (exception):
    return re.findall("dev='(\S*)'", exception.output)

# Help printing function
def print_help():
  print ("Usage: " + sys.argv[0] + " Image_File [Write Speed] [/path/to/burner]")
  print ("Acceptable image formats are Discjuggler (CDI), Nero (nrg), ISO, and BIN/CUE.")
  print ("Write speed and burner path are optional. If omitted, lowest speed and the burner at " + drive_path + " is used.")
  print ("All burner paths can be found by running 'wodim --devices'.")

# Asks user a yes / no question and quits if the user says no. Default question formatted to fit below a "WARNING: ... " string
def ask_for_continue(question = "         Would you like to continue (Y/n)? "):
  to_continue = string.lower(raw_input(question))
  if to_continue != "" and to_continue[0] == 'n':
    exit(1)

# Delete the temp dir if it already exists and create it again
def prepare_temp():
  print ("Clearing Temp Directory")
  if os.path.isdir('/tmp/bootdreams'):
    shutil.rmtree('/tmp/bootdreams', True)
  os.mkdir('/tmp/bootdreams')


# Drive index
try:
  drive_path = sys.argv[3]
except IndexError:
  try:
    drive_path = query_burners()[0]
  except IndexError:
    print ("Warning: No burner in system. A burner is obviously required.")
    exit(1)

# The file to process
try:
  user_input = sys.argv[1]
except IndexError:
  print ("ERROR: No File Specified.")
  print_help()
  sys.exit(1)

# Burn Speed
try:
  burn_speed = sys.argv[2]
except IndexError:
  burn_speed = 0



# See if user was trying to get help
if string.lower(user_input) == "help" or string.lower(user_input) == "--help" or string.lower(user_input) == "-h":
  print_help()
  sys.exit(1)

# Split the user input into path and filename
# input_image is always exactly what the user passed
split_path = os.path.split(user_input)
input_dir  = split_path[0]
input_file = split_path[1]
input_image = user_input

# See what programs the user has installed to determine what can be handled
avail_tools = []

# A tool borrowed from Jay on SackOverflow: http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
# Takes a program name and attempts to determine if it exists either in the current directory or in the PATH.
# Returns the program full location if it exists, None if it doesn't.
def which(program):
  def is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return exe_file
  return None

# Simple function to check for existence of tools.
# Sees if the file exists and is executable and returns the program name in a list if it is.
# If it is not, it tells the user about it and returns an empty list
def check_prog(prog, img_format):
  if which(prog):
    return [prog]
  else:
    print    ("Warning: " + prog + " tool not installed. Will not be able to burn " + img_format + " images.")
    if prog == "cdirip" or prog == "nerorip":
      print ("         Run make && sudo make install in the root bootdreams.py folder to install them from the included source.")
    else:
      print ("         Please install the " + prog + " program from your distribution's repositories")
    return []

#Fill in the list of available tools
avail_tools += check_prog("nerorip", "Nero")
avail_tools += check_prog("cdirip", "DiscJugler")
avail_tools += check_prog("bchunk", "BIN/CUE")


# Make sure file exists
if not os.path.isfile(input_image):
  print ("ERROR: File not found.")
  print_help()
  sys.exit(1)

# Convert extension to lower case to properly handle it
input_ext = string.lower(input_image[-3:])

# CDI AND NRG FILE HANDLING
if input_ext == "cdi" or input_ext == "nrg":
  # Set some CDI / NRG specific options here
  
  # Default for discjuggler
  image_type = "DiscJuggler"
  image_info_call = ["cdirip", input_image, "-info"]
  
  # Special case for nero
  if input_ext == "nrg":
    image_type = "Nero"
    image_info_call = ["nerorip", "-i", input_image]
  
  # Print some helpful information
  print ("Going to burn " + image_type + " image " + input_image + " at " + str(burn_speed) + "x on burner at " + drive_path)
  
  # Get information about this image file
  image_info = subprocess.Popen(image_info_call, stdout=subprocess.PIPE).communicate()[0]
  
  # Make a list containing lists of track types for each session.
  # First dimension is Session number, second is Track number
  session_data = []
  
  print ("Getting Session and Track information")
  
  # Split the image_info string by the Session i has d track(s) string. Discard the first because it offers no data
  for i in re.split('Session \d+ has \d+ track\(s\)', image_info)[1:]:
    # Get all the track types in a list and append it to the list of session data
    session_data.append(re.findall('Type: (\S*)', i))
  
  # Check for situations to warn the user about:
  # More than 2 sessions:
  if len(session_data) > 2:
    print ("Warning: Image has more than 2 sessions. Continuing anyway though this is untested.")
  
  # Unsupported session type
  for s in session_data:
    for t in s:
      if not t in ["Mode1/2048", "Mode2/2336", "Mode2/2352", "Audio/2352"]:
        print ("ERROR: Unsupported session type " + t + ". Only Mode1/2048, Mode2/2336, Mode2/2352, and Audio/2352 are supported.")
        exit(1)
  
  # data/data image with CDDA
  if session_data[0] == ["Mode2/2336", "Audio/2352"]:
    print ("Warning: CDRecord cannot properly burn a data/data DiscJuggler image with CDDA.")
    print ("         You can continue anyway though it may be a coaster if there is very little space left in the image.")
    ask_for_continue()
  
  # Prepare the temp directory
  prepare_temp()
  
  # Rip the Image
  print ("Ripping " + input_ext + " image")
  print ("")
  
  # The last version (which did not fail to burn any images for me) did this bit wrong and only -iso was ever passed to cdirip.
  # It never got the -cut and -cutall options which together don't work the way the readme says they should.
  # Just going to make it not -cutall and fix it if a user tells me they had a bad burn that would have been fixed by it
  rip_options = []
  if input_ext == "cdi":
    rip_options = ["cdirip", input_image, "/tmp/bootdreams", "-iso"]
    if session_data[0][0] != "Audio/2352":
      rip_options += ["-cut"]
    else:
      rip_options += ["-full"]
  else:
    rip_options = ["nerorip"]
    if session_data[0][0] != "Audio/2352":
      rip_options += ["--trim"]
    else:
      rip_options += ["--full"]
    rip_options += [input_image, "/tmp/bootdreams"]
    
  if subprocess.call(rip_options) != 0:
    print ("ERROR: " + input_ext + "rip failed to extract image data. Please check its output for more information.")
    exit(1)
  
  # Burn the CD
  if do_burn:
    print ("Burning CD")
  print ("")
  index = 1
  for s in session_data:
    cdrecord_opts = []
    for t in s:
      if t == "Mode1/2048":
        cdrecord_opts += ["-data", "/tmp/bootdreams/tdata" + str(index).zfill(2) + ".iso"]
      elif t == "Mode2/2336" or t == "Mode2/2352":
        cdrecord_opts += ["-xa", "/tmp/bootdreams/tdata" + str(index).zfill(2) + ".iso"]
      elif t == "Audio/2352":
        cdrecord_opts += ["-audio", "/tmp/bootdreams/taudio" + str(index).zfill(2) + ".wav"]
      index += 1
      
    # Build options list for cdrecord
    cdrecord_call = ["cdrecord", "-dev=" + str(drive_path), "gracetime=2", "-v", "driveropts=burnfree", "speed=" + str(burn_speed)]
    if index == len(session_data) + 1:
      cdrecord_call.append("-eject")
    else:
      cdrecord_call.append("-multi")
    if "-xa" in cdrecord_opts or "-data" in cdrecord_opts:
      cdrecord_call.append("-tao")
    else:
      cdrecord_call.append("-dao")
    cdrecord_call += cdrecord_opts
    
    if not do_burn:
      print(cdrecord_call)
    
    # Burn the session
    if do_burn and subprocess.call(cdrecord_call) != 0:
      print ("ERROR: CDRecord failed. Please check its output for more information.")
      exit(1)
  
  if do_burn:
    print ("Image burn complete.")
    
    
elif input_ext == "bin" or input_ext == "cue":
  # Run bchunk on this file to get its iso then let the iso burning section handle it
  print ("Converting a BIN/CUE image to ISO")
 
  prepare_temp()
  
  # Find both the BIN and CUE file
  bin_file = input_file
  cue_file = input_file
  base_file = input_file[:-3]
  
  # Scans the input_dir for a file matching the passed pattern concatenated on to the end of the base_file
  def find_file(pattern):
    for f in os.listdir(input_dir):
      if re.match(base_file + pattern, f):
        return f
  
  # Find the matching pair to this bin / cue file
  if input_ext == "bin":
    cue_file = find_file("[cC][uU][eE]")
  else:
    bin_file = find_file("[bB][iI][nN]")
  
  # Check the cue file for session information and build a list
  session_data = []
  cue = open(input_dir + "/" + cue_file, "r")
  for line in cue:
    t = re.match(r" *TRACK \d+ (\w+/\d+)", line)
    if t:
      session_data += [t.group(1)]
  print session_data
  
  # Build call to bchunk
  bchunk_call = ["bchunk", input_dir + "/" + bin_file, input_dir + "/" + cue_file, "/tmp/bootdreams/" + base_file]
  
  # Call bchunk
  #if subprocess.call(bchunk_call) != 0:
  #  print ("ERROR: bchunk failed. Please check its output for more information.")
  #  exit(1)
  
elif input_ext == "iso":
  
  # TODO: Isos have checkbox for multisesion and menu option for record mode: mode1 or mode 2 form 1
  cdrecord_call = ['cdrecord', 'dev=' + str(drive_path), 'gracetime=2', '-v', 'driveropts=burnfree', 'speed=' + str(burn_speed), '-eject', '-tao']
  if iso_multi == True:
    cdrecord_call += ['-multi']
  if iso_mode1 == True:
    cdrecord_call += ['-data']
  else:
    cdrecord_call += ['-xa']
  cdrecord_call += [input_image]
  
  print (cdrecord_call)
