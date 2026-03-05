#!/usr/bin/env python3
"""Listens for presenterm UDP events and executes speaker note directives.

Directives create/close tmux panes and type commands into them.

Usage: python3 slide-follower.py <slides.md> <session-name>

Requires: tmux
"""

import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

LISTEN_ADDR = "127.255.255.255"
LISTEN_PORT = 59418

NOTE_START_RE = re.compile(r"^<!-- speaker_note:\s*$")
NOTE_END_RE = re.compile(r"^-->$")
DIRECTIVE_RE = re.compile(r"^(pane|type|wait|close)\s+(.+)$")
KILL_RE = re.compile(r"^kill$")


def parse_slides(path: Path) -> dict[int, list[str]]:
    """Parse slides and return mapping of slide number to list of directive lines.

    Presenterm's slide numbering:
      - Slide 1: title slide (auto-generated from front matter)
      - Slide 2+: content slides separated by <!-- end_slide --> markers
    """
    notes: dict[int, list[str]] = {}
    text = path.read_text()
    lines = text.splitlines()

    # Skip front matter (--- to ---), which is slide 1
    i = 0
    if i < len(lines) and lines[i] == "---":
        i += 1
        while i < len(lines) and lines[i] != "---":
            i += 1
        i += 1  # skip closing ---

    # Parse remaining slides starting at slide 2
    current_slide = 2
    in_note = False
    current_directives: list[str] = []

    for line in lines[i:]:
        if line == "<!-- end_slide -->":
            if in_note:
                # Close unclosed note at slide boundary
                if current_directives:
                    notes[current_slide] = current_directives
                in_note = False
                current_directives = []
            current_slide += 1
            continue

        if NOTE_START_RE.match(line):
            in_note = True
            current_directives = []
            continue

        if in_note:
            if NOTE_END_RE.match(line):
                if current_directives:
                    notes[current_slide] = current_directives
                in_note = False
                current_directives = []
                continue
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                current_directives.append(stripped)

    # Handle note at end of file (last slide, no trailing end_slide)
    if in_note and current_directives:
        notes[current_slide] = current_directives

    return notes


AUTO_DELAY = 1.0  # seconds between directives


def execute_directives(
    directives: list[str],
    session: str,
    panes: dict[str, str],
) -> None:
    """Execute a list of directives, managing tmux panes."""
    for i, line in enumerate(directives):
        if i > 0:
            time.sleep(AUTO_DELAY)
        if KILL_RE.match(line):
            print("  Killing tmux session", file=sys.stderr)
            subprocess.run(["tmux", "kill-session", "-t", session], check=False)
            return

        m = DIRECTIVE_RE.match(line)
        if not m:
            print(f"  Ignoring unknown directive: {line}", file=sys.stderr)
            continue

        action = m.group(1)
        args = m.group(2)

        if action == "pane":
            name, _, cmd = args.partition(" ")
            if not cmd:
                print(
                    f"  Error: pane directive needs a command: {line}", file=sys.stderr
                )
                continue
            create_pane(session, name, cmd, panes)

        elif action == "type":
            name, _, text = args.partition(" ")
            if not text:
                print(f"  Error: type directive needs text: {line}", file=sys.stderr)
                continue
            type_into_pane(name, text, panes)

        elif action == "wait":
            try:
                secs = float(args)
            except ValueError:
                print(f"  Error: invalid wait duration: {args}", file=sys.stderr)
                continue
            print(f"  Waiting {secs}s", file=sys.stderr)
            time.sleep(secs)

        elif action == "close":
            name = args.strip()
            close_pane(name, panes)


def create_pane(
    session: str,
    name: str,
    cmd: str,
    panes: dict[str, str],
) -> None:
    """Create a new tmux pane running cmd."""
    if name in panes:
        print(f"  Pane '{name}' already exists, closing first", file=sys.stderr)
        close_pane(name, panes)

    # Determine split target:
    # - If no right-side panes exist: split horizontally from presenterm pane
    # - If right-side panes exist: split vertically from the last existing pane
    if not panes:
        split_args = ["tmux", "split-window", "-h", "-t", f"{session}:0.0"]
    else:
        last_pane_id = list(panes.values())[-1]
        split_args = ["tmux", "split-window", "-v", "-t", last_pane_id]

    # Keep pane alive if the command exits (e.g. SSH connection failure)
    split_args.extend(["-P", "-F", "#{pane_id}", f"{cmd}; exec bash"])

    print(f"  Creating pane '{name}': {cmd}", file=sys.stderr)
    result = subprocess.run(split_args, capture_output=True, text=True, check=True)
    pane_id = result.stdout.strip()
    panes[name] = pane_id
    print(f"  Pane '{name}' created with id {pane_id}", file=sys.stderr)


def type_into_pane(name: str, text: str, panes: dict[str, str]) -> None:
    """Type text into a named pane and press Enter."""
    pane_id = panes.get(name)
    if not pane_id:
        print(f"  Error: no pane named '{name}'", file=sys.stderr)
        return

    print(f"  Typing into '{name}': {text[:80]}...", file=sys.stderr)
    result = subprocess.run(["tmux", "send-keys", "-t", pane_id, "-l", text])
    if result.returncode != 0:
        print(f"  Warning: send-keys failed for pane '{name}'", file=sys.stderr)
        return
    subprocess.run(["tmux", "send-keys", "-t", pane_id, "Enter"])


def close_pane(name: str, panes: dict[str, str]) -> None:
    """Close a named pane."""
    pane_id = panes.pop(name, None)
    if not pane_id:
        print(f"  Warning: no pane named '{name}' to close", file=sys.stderr)
        return

    print(f"  Closing pane '{name}' ({pane_id})", file=sys.stderr)
    subprocess.run(["tmux", "kill-pane", "-t", pane_id], check=False)


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <slides.md> <session-name>", file=sys.stderr)
        sys.exit(1)

    slides_path = Path(sys.argv[1])
    session = sys.argv[2]

    if not slides_path.is_file():
        print(f"Error: slides file not found: {slides_path}", file=sys.stderr)
        sys.exit(1)

    notes = parse_slides(slides_path)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((LISTEN_ADDR, LISTEN_PORT))

    print(
        f"Listening for presenterm events on UDP port {LISTEN_PORT}...", file=sys.stderr
    )
    print(f"Slides file: {slides_path}", file=sys.stderr)
    print(f"Session: {session}", file=sys.stderr)
    print(f"Parsed {len(notes)} slides with directives", file=sys.stderr)

    panes: dict[str, str] = {}
    executed: set[int] = set()

    while True:
        data, _ = sock.recvfrom(4096)
        try:
            event = json.loads(data)
            slide = event["event"]["slide"]
        except (json.JSONDecodeError, KeyError):
            continue

        if slide in executed:
            continue

        directives = notes.get(slide)
        if directives:
            executed.add(slide)
            print(
                f"[slide {slide}] Executing {len(directives)} directives",
                file=sys.stderr,
            )
            execute_directives(directives, session, panes)
        else:
            executed.add(slide)
            print(f"[slide {slide}] No directives", file=sys.stderr)


if __name__ == "__main__":
    main()
