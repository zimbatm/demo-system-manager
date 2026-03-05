#!/usr/bin/env bash
# Listens for presenterm UDP events and types speaker notes into Claude's tmux pane.
#
# Usage: bash slide-follower.sh <slides.md> <tmux-target-pane>
#
# Requires: socat, jq, tmux
set -euo pipefail

slides_file="${1:?Usage: slide-follower.sh <slides.md> <tmux-target-pane>}"
target_pane="${2:?Usage: slide-follower.sh <slides.md> <tmux-target-pane>}"

if [[ ! -f "$slides_file" ]]; then
  echo "Error: slides file not found: $slides_file" >&2
  exit 1
fi

# Extract the speaker note for a given slide number (1-based, matching presenterm).
# Slide 1 is the title slide (front matter). Subsequent slides are separated by
# <!-- end_slide --> markers. Speaker notes are <!-- speaker_note: ... --> comments.
extract_note() {
  local target_slide="$1"
  local current_slide=1
  local in_frontmatter=false
  local note=""

  while IFS= read -r line; do
    # Skip front matter (slide 1: title)
    if [[ "$current_slide" -eq 1 ]]; then
      if [[ "$line" == "---" ]]; then
        if "$in_frontmatter"; then
          current_slide=2
          note=""
        else
          in_frontmatter=true
        fi
      fi
      continue
    fi

    if [[ "$line" == '<!-- end_slide -->' ]]; then
      if [[ "$current_slide" -eq "$target_slide" ]]; then
        break
      fi
      current_slide=$((current_slide + 1))
      note=""
      continue
    fi

    if [[ "$line" =~ ^'<!-- speaker_note: '(.*)' -->'$ ]]; then
      note="${BASH_REMATCH[1]}"
    fi
  done < "$slides_file"

  # Handle the last slide (no trailing end_slide marker)
  if [[ "$current_slide" -eq "$target_slide" ]]; then
    echo "$note"
  fi
}

echo "Listening for presenterm events on UDP port 59418..." >&2
echo "Slides file: $slides_file" >&2
echo "Target pane: $target_pane" >&2

socat -u UDP-RECV:59418,bind=127.255.255.255,reuseaddr - | while IFS= read -r event; do
  # Parse the slide number from the JSON event
  slide=$(echo "$event" | jq -r '.event.slide // empty' 2>/dev/null)

  if [[ -z "$slide" ]]; then
    continue
  fi

  note=$(extract_note "$slide")

  if [[ -n "$note" ]]; then
    echo "[slide $slide] Sending to Claude: $note" >&2
    tmux send-keys -t "$target_pane" "$note" Enter
  else
    echo "[slide $slide] No speaker note" >&2
  fi
done
