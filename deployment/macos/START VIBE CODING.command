#!/bin/bash
# Start the Vibe Coding classroom (macOS).
# First time: see MAC-README-FIRST.txt for the one-time Gatekeeper step.
cd "$(dirname "$0")" || exit 1
exec bash ./vibe-macos.sh start
