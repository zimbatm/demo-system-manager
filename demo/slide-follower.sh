#!/usr/bin/env bash
# Listens for presenterm UDP events and writes speaker notes to .current-note
#
# Usage: bash slide-follower.sh [slides.md]
#
# Requires: socat, jq
set -euo pipefail

slides_file="${1:-slides.md}"

if [[ ! -f "$slides_file" ]]; then
  echo "Error: slides file not found: $slides_file" >&2
  exit 1
fi

# Extract the speaker note for a given slide index (0-based).
# Slides are separated by <!-- end_slide --> markers.
# Speaker notes are <!-- speaker_note: ... --> comments within a slide.
extract_note() {
  local slide_index="$1"
  local current_slide=0
  local note=""

  while IFS= read -r line; do
    if [[ "$line" =~ ^'<!-- end_slide -->'$ ]]; then
      if [[ "$current_slide" -eq "$slide_index" ]]; then
        break
      fi
      current_slide=$((current_slide + 1))
      note=""
      continue
    fi

    if [[ "$line" =~ ^'<!-- speaker_note: '\"(.*)\"' -->'$ ]]; then
      note="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^'<!-- speaker_note: '(.*)' -->'$ ]]; then
      note="${BASH_REMATCH[1]}"
    fi
  done < "$slides_file"

  # Handle the last slide (no trailing end_slide)
  if [[ "$current_slide" -eq "$slide_index" ]]; then
    echo "$note"
  fi
}

echo "Listening for presenterm events on UDP port 59418..." >&2
echo "Slides file: $slides_file" >&2

socat -u UDP-RECV:59418,bind=127.255.255.255,reuseaddr - | while IFS= read -r event; do
  # Parse the slide number from the JSON event
  slide=$(echo "$event" | jq -r '.event.slide // empty' 2>/dev/null)

  if [[ -z "$slide" ]]; then
    continue
  fi

  # Account for the front-matter/title slide: presenterm uses slide 0
  # for the title (generated from front matter), so the first <!-- end_slide -->
  # separated content is slide 1 in presenterm's numbering.
  note=$(extract_note "$slide")

  if [[ -n "$note" ]]; then
    echo "$note" > .current-note
    echo "[slide $slide] Updated .current-note: $note" >&2
  else
    echo "[slide $slide] No speaker note" >&2
  fi
done
