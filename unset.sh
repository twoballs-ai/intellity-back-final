#!/bin/bash

# Function to unset a variable
unset_var() {
  var_name=$1
  unset $var_name
}

# Read the .env file and unset variables
if [ -f .env ]; then
  while IFS= read -r line; do
    # Ignore comments and empty lines
    if [[ ! $line =~ ^# && ! -z $line ]]; then
      var_name=$(echo "$line" | cut -d '=' -f 1 | xargs)
      unset_var $var_name
    fi
  done < .env
fi

echo "Environment variables have been reset."