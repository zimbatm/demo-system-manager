#!/usr/bin/env bash
# Launch the demo: presenterm full-width.
# Slide-follower runs in a background tmux window and creates panes dynamically
# as directed by speaker notes.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
session="demo"

# Start tmux with just presenterm (full width)
tmux new-session -d -s "$session" -x "$(tput cols)" -y "$(tput lines)" \
  "presenterm --publish-speaker-notes ${script_dir}/slides.md"

# Run slide-follower in a background window
tmux new-window -d -t "$session" -n "follower" \
  "python3 '${script_dir}/slide-follower.py' '${script_dir}/slides.md' '${session}'"

tmux attach -t "$session"
