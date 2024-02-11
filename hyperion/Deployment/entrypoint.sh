#!/bin/bash
set -e

# Check if LAUNCH_ON_STARTUP is true and execute start.sh
if [ "$HYPERION_LAUNCH_ON_STARTUP" = "true" ]; then
    echo "Launching start.sh on startup..."
    bash run.sh wax-indexer
    # tail -f /apps/wax/stderr.txt
else
    echo "LAUNCH_ON_STARTUP is not true, skipping start.sh execution."
    tail -f /dev/null
fi