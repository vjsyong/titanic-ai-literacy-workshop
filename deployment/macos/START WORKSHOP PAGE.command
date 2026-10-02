#!/bin/bash
# Start or reopen just the workshop web page.
cd "$(dirname "$0")" || exit 1
exec bash ./vibe-macos.sh start-page
