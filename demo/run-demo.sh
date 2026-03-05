#!/usr/bin/env bash
# Launch the demo: presenterm on the left, Claude Code on the right,
# with slide-follower bridging them via .current-note.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Start tmux with two panes
# Left pane:  presenterm (slides)
# Right pane: slide-follower (background) + claude
tmux new-session -d -s demo -x "$(tput cols)" -y "$(tput lines)" \
  "presenterm --publish-speaker-notes ${script_dir}/slides.md" \; \
  split-window -h \
  "bash ${script_dir}/slide-follower.sh ${script_dir}/slides.md & claude; exec bash" \; \
  attach
