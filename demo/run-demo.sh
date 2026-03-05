#!/usr/bin/env bash
# Launch the demo: presenterm on the left, Claude Code on the right,
# with slide-follower typing speaker notes directly into Claude's pane.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
session="demo"

# Start tmux with two panes
# Left pane (0):  presenterm (slides)
# Right pane (1): claude
tmux new-session -d -s "$session" -x "$(tput cols)" -y "$(tput lines)" \
  "presenterm --publish-speaker-notes ${script_dir}/slides.md"
tmux split-window -h -t "$session" "claude; exec bash"

# Start slide-follower in the background, targeting the Claude pane
bash "${script_dir}/slide-follower.sh" "${script_dir}/slides.md" "${session}:0.1" &

tmux attach -t "$session"

# Clean up the slide-follower when tmux exits
kill %1 2>/dev/null || true
