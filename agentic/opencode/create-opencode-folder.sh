#!/bin/bash

# Create a random folder in /tmp with current time format yymmdd-hhmmss-*
TIMESTAMP=$(date +%y%m%d-%H%M%S)
RANDOM_SUFFIX=$(head -c 5 /dev/urandom | base32 | tr -d '=' | tr '[:upper:]' '[:lower:]')
FOLDER_NAME="${TIMESTAMP}-${RANDOM_SUFFIX}"

# Create the directory
mkdir -p "/tmp/${FOLDER_NAME}"

# Change to the directory
cd "/tmp/${FOLDER_NAME}" || exit 1

# Run opencode
opencode