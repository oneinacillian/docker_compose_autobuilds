#!/bin/bash

docker exec -d node bash start.sh
sleep 10
docker exec -d hyperion bash run.sh wax-indexer
