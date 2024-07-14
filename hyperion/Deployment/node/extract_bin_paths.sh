#!/bin/bash

# Function to extract the path of nodeos from a .deb package
extract_bin_path() {
    local deb_file=$1
    dpkg-deb -c "$deb_file" | awk '{print $6}' | grep -E '(bin/nodeos)$' | while read -r line; do
        # Remove the leading './' if it exists and extract the directory path
        echo "/${line#./}" | sed 's:/nodeos$::'
        return
    done
}

# Check if the package file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <path-to-deb-package>"
    exit 1
fi

DEB_PACKAGE=$1

# Extract the path
BIN_PATH=$(extract_bin_path "$DEB_PACKAGE")

# Check if the path was found
if [ -z "$BIN_PATH" ]; then
    echo "Path for nodeos not found in the package. Exiting."
    exit 1
fi

echo "NODEOSBINDIR=$BIN_PATH"
