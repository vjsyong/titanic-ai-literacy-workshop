#!/bin/bash
# Remove the managed classroom runtime and the stored API key.
cd "$(dirname "$0")" || exit 1
exec bash ./vibe-macos.sh reset-env
