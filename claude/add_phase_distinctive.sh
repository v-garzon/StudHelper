#!/bin/bash

# Directory containing the files
TARGET_DIR="claude"
# Prefix to add
PREFIX="02_"

# Check if directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Loop through all files (not directories) in the folder
for file in "$TARGET_DIR"/*; do
    if [ -f "$file" ]; then
        base=$(basename "$file")
        mv "$file" "$TARGET_DIR/$PREFIX$base"
    fi
done