#!/bin/bash

docker-compose down
CURRENT_DIR=$(basename "$(pwd)")

# List of volume names you want to remove
VOLUME_NAMES=("node" "esdata1" "esdata2" "esdata3" "rabbitmqdata" "redisdata" "hyperiondata")

# Loop through the volume names and remove them
for VOLUME_NAME in "${VOLUME_NAMES[@]}"; do
  #echo "${CURRENT_DIR}_${VOLUME_NAME}"
  docker volume rm "${CURRENT_DIR}_${VOLUME_NAME}"
done

#docker system prune -a --volumes