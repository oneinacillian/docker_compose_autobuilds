#!/bin/bash
set -e

# Check if LAUNCH_ON_STARTUP is true and execute start.sh
if [ "$HYPERION_LAUNCH_ON_STARTUP" = "true" ]; then

    wait_for_service() {
        host="$1"
        port="$2"
        echo "Waiting for ${host}:${port}..."
        while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}"; do   
            echo "Waiting for ${host}:${port}..."
            sleep 2
        done
        echo "${host}:${port} is available."
    }

    # Wait for RabbitMQ, Elasticsearch, and Redis
    wait_for_service rabbitmq 5672
    wait_for_service es1 9200
    wait_for_service es2 9200
    wait_for_service es3 9200
    wait_for_service redis 6379
    wait_for_service node 8888
    wait_for_service node 9876

    echo "Launching start.sh on startup..."
    bash run.sh wax-indexer
    # tail -f /apps/wax/stderr.txt
else
    echo "LAUNCH_ON_STARTUP is not true, skipping start.sh execution."
    tail -f /dev/null
fi