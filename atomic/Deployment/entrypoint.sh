#!/bin/bash
set -e

# Navigate to the working directory
cd /app/eosio-contract-api

# Check if START_ON_LAUNCH is true and execute the pm2 command
if [ "$ATOMIC_LAUNCH_ON_STARTUP" = "true" ]; then
    echo "Starting pm2 with eosio-contract-api-filler..."
    pm2 start ecosystems.config.json --only eosio-contract-api-filler
    # Keep pm2 running in the foreground to prevent the container from exiting
    pm2 logs --raw
else
    echo "START_ON_LAUNCH is not true, skipping pm2 execution."
    # Here you can also provide an alternative command to keep the container running, or exit
    # For example, to keep the container running: tail -f /dev/null
    tail -f /dev/null
fi
