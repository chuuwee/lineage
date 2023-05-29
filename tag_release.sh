#!/bin/bash

# Check if a version string is provided
if [ -z "$1" ]
then
    echo "Error: No version string provided."
    echo "Usage: $0 version-string"
    exit 1
fi

# Define the version string
version_string="$1"

# Rewrite the version.py file
echo "VERSION = '$version_string'" > scripts/version.py

# Add the file to the git repository
git add scripts/version.py

# Commit the changes
git commit -m "release: v$version_string"

# Tag this commit
git tag "v$version_string"

# Push the commit and tags
git push origin "v$version_string"
git push
