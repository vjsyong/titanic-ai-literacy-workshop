#!/bin/bash
# Restore the workshop scripts and data to their original state.
cd "$(dirname "$0")" || exit 1
exec bash ./vibe-macos.sh reset-workshop
