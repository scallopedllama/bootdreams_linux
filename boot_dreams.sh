#!/bin/bash
# Usage: bootdreams image_file.iso /path/to/burner [speed]


# Make sure cdrecord installed
#if [ ! -e 'cdrecord' ]
#  then
#  echo "In order to burn DC games, cdrecord must be installed and properly configured."
#  echo "Please consult your distribution's documentation."
#  exit 1
#fi

# Get image extension
ext=`echo $1 | awk -F . '{print tolower($NF)}'`
case "$ext" in

  cdi)
    ;;
  iso)
    ;;
  cue)
    ;;
  *)
    echo "The specified image with the $ext extension is currently unsupported."
    echo "Only CDI, ISO, and CUE formats are supported."
    exit 1
    ;;

esac
