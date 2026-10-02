#!/bin/bash
# Rebuild the classroom runtimes without touching student project files.
cd "$(dirname "$0")" || exit 1
exec bash ./vibe-macos.sh repair
