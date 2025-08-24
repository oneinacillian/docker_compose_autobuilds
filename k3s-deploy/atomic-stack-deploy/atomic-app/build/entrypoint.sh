#!/bin/bash
set -e

# Navigate to the working directory
cd /app/eosio-contract-api

# Function to wait for services
wait_for_service() {
    echo "Checking availability of $1:$2"
    timeout 60 bash -c "until echo > /dev/tcp/$1/$2; do sleep 1; done"
    if [ $? -ne 0 ]; then
        echo "Service $1:$2 did not become available"
        exit 1
    fi
    echo "$1:$2 is available"
}

# Wait for required services
wait_for_service redis 6379
wait_for_service postgres 5432

echo "All required services are available. Starting Atomic application..."

# Start the application with PM2
echo "Starting pm2 with eosio-contract-api-filler..."
pm2 start ecosystems.config.json --only eosio-contract-api-filler

# Keep pm2 running in the foreground
pm2 logs --raw
