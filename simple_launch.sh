#!/bin/bash

# Setting initial command
factorio_command="/opt/factorio/bin/x64/factorio"

# TODO Adding this because of bug, will need to be removed once bug in factorio is fixed
cd /opt/factorio/saves
# Handling save settings
save_dir="/opt/factorio/saves"
if [ -z $FACTORIO_SAVE ]
then
  if [ "$(ls -A $save_dir)" ]
  then
    echo "###"
    echo "# Taking latest save"
    echo "###"
  else
    echo "###"
    echo "# Creating a new map [save.zip]"
    echo "###"
    /opt/factorio/bin/x64/factorio --create save.zip
  fi
  factorio_command="$factorio_command --start-server-load-latest --server-settings /opt/factorio/data/server-settings.json"
else
  factorio_command="$factorio_command --start-server $FACTORIO_SAVE"
fi
echo "###"
echo "# Launching Game"
echo "###"
# Closing stdin
exec 0<&-
exec $factorio_command
