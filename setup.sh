#!/bin/bash

# Check for existing saves files
if [ -f "saves.tar.gz" ]; then
    # Will unpack if exists
    tar -xvzf saves.tar.gz
fi

# Setup config
cp docker-compose-example.yml docker-compose.yml
cp server-settings.example.json server-settings.json
mkdir -p ./mods
mkdir -p ./saves
