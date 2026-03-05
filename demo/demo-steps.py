#!/usr/bin/env python3
"""Demo step driver: manages tmux session, presenterm, and step directives.

Usage:
    python3 demo-steps.py start     -- create tmux session with presenterm + claude
    python3 demo-steps.py next      -- advance one slide, execute directives
    python3 demo-steps.py reset     -- reset state to step 0
    python3 demo-steps.py status    -- print current step info
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
STEPS_FILE = SCRIPT_DIR / "steps.yaml"
STATE_FILE = Path("/tmp/demo-state.json")
SESSION = "demo"
CREDENTIALS_FILE = Path.home() / ".claude" / ".credentials.json"

DIRECTIVE_RE = re.compile(r"^(pane|type|wait|wait-for|close|exec|style)\s+(.+)$")
KILL_RE = re.compile(r"^kill$")

AUTO_DELAY = 1.0  # seconds between directives
WAIT_FOR_POLL = 0.5  # seconds between polls


# -- API key resolution -------------------------------------------------------


def resolve_api_key() -> str | None:
    """Resolve ANTHROPIC_API_KEY from env or Claude Code credentials file."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key

    if CREDENTIALS_FILE.exists():
        try:
            creds = json.loads(CREDENTIALS_FILE.read_text())
            token = creds.get("claudeAiOauth", {}).get("accessToken")
            if token:
                print("  Using API key from Claude credentials", file=sys.stderr)
                return token  # type: ignore[no-any-return]
        except (json.JSONDecodeError, KeyError):
            pass

    return None


def expand_directives(directives: list[str]) -> list[str]:
    """Expand $ANTHROPIC_API_KEY in directive strings."""
    key = resolve_api_key()
    if key is None:
        return directives
    return [d.replace("$ANTHROPIC_API_KEY", key) for d in directives]


# -- State management ---------------------------------------------------------


def load_state() -> dict[str, object]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())  # type: ignore[return-value]
    return {"step": 0, "panes": {}}


def save_state(state: dict[str, object]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


# -- tmux helpers (from slide-follower.py) ------------------------------------


def create_pane(
    session: str,
    name: str,
    cmd: str,
    panes: dict[str, str],
) -> None:
    if name in panes:
        print(f"  Pane '{name}' already exists, closing first", file=sys.stderr)
        close_pane(name, panes)

    # Panes other than the initial "claude" control pane
    demo_panes = {k: v for k, v in panes.items() if k != "claude"}
    if not demo_panes:
        # First demo pane: split right of presenterm
        split_args = ["tmux", "split-window", "-h", "-t", f"{session}:0.0"]
    else:
        # Stack below the last demo pane
        last_pane_id = list(demo_panes.values())[-1]
        split_args = ["tmux", "split-window", "-v", "-t", last_pane_id]

    split_args.extend(["-P", "-F", "#{pane_id}", cmd])

    print(f"  Creating pane '{name}': {cmd}", file=sys.stderr)
    result = subprocess.run(split_args, capture_output=True, text=True, check=True)
    pane_id = result.stdout.strip()
    panes[name] = pane_id
    print(f"  Pane '{name}' created with id {pane_id}", file=sys.stderr)


def type_into_pane(name: str, text: str, panes: dict[str, str]) -> None:
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
    pane_id = panes.pop(name, None)
    if not pane_id:
        print(f"  Warning: no pane named '{name}' to close", file=sys.stderr)
        return

    print(f"  Closing pane '{name}' ({pane_id})", file=sys.stderr)
    subprocess.run(["tmux", "kill-pane", "-t", pane_id], check=False)


def wait_for_pane(name: str, pattern: str, panes: dict[str, str]) -> None:
    pane_id = panes.get(name)
    if not pane_id:
        print(f"  Error: no pane named '{name}'", file=sys.stderr)
        return

    compiled = re.compile(pattern)
    print(f"  Waiting for '{pattern}' in pane '{name}'...", file=sys.stderr)

    while True:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", pane_id],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and compiled.search(result.stdout):
            print(f"  Pattern matched in pane '{name}'", file=sys.stderr)
            return
        time.sleep(WAIT_FOR_POLL)


# -- Directive execution ------------------------------------------------------


def execute_directives(
    directives: list[str],
    session: str,
    panes: dict[str, str],
) -> None:
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

        elif action == "wait-for":
            name, _, pattern = args.partition(" ")
            if not pattern:
                print(f"  Error: wait-for needs a pattern: {line}", file=sys.stderr)
                continue
            wait_for_pane(name, pattern, panes)

        elif action == "exec":
            cmd = args
            print(f"  Exec: {cmd[:80]}...", file=sys.stderr)
            subprocess.run(cmd, shell=True, check=True)

        elif action == "style":
            name, _, style = args.partition(" ")
            pane_id = panes.get(name)
            if not pane_id:
                print(f"  Error: no pane named '{name}'", file=sys.stderr)
                continue
            print(f"  Styling pane '{name}': {style}", file=sys.stderr)
            subprocess.run(
                ["tmux", "select-pane", "-t", pane_id, "-P", style], check=False
            )

        elif action == "close":
            name = args.strip()
            close_pane(name, panes)


# -- Subcommands --------------------------------------------------------------


def load_steps() -> list[dict[str, object]]:
    data = yaml.safe_load(STEPS_FILE.read_text())
    return data["steps"]  # type: ignore[no-any-return]


def cmd_next() -> None:
    steps = load_steps()
    state = load_state()
    step_index: int = state["step"]  # type: ignore[assignment]
    panes: dict[str, str] = state.get("panes", {})  # type: ignore[assignment]

    if step_index >= len(steps):
        print("No more steps.", file=sys.stderr)
        sys.exit(1)

    step = steps[step_index]
    name: str = step["name"]  # type: ignore[assignment]
    description: str = step.get("description", "")  # type: ignore[assignment]
    directives: list[str] = step.get("directives", [])  # type: ignore[assignment]

    # Advance presenterm
    print("  Advancing slide...", file=sys.stderr)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0.0", "Right"], check=False)

    print(
        f"[step {step_index + 1}/{len(steps)}] {name}: {description}", file=sys.stderr
    )

    if directives:
        directives = expand_directives(directives)
        execute_directives(directives, SESSION, panes)

    state["step"] = step_index + 1
    state["panes"] = panes
    save_state(state)

    # Output for Claude to read
    remaining = len(steps) - step_index - 1
    print(f"Step {step_index + 1}/{len(steps)}: {name} -- {description}")
    if remaining > 0:
        next_step = steps[step_index + 1]
        print(f"Next: {next_step['name']} -- {next_step.get('description', '')}")
    else:
        print("Demo complete.")


def cmd_start(step: int = 0) -> None:
    """Create tmux session with presenterm + claude, write initial state."""
    steps = load_steps()
    if step > len(steps):
        print(f"Error: step {step} out of range (max {len(steps)})", file=sys.stderr)
        sys.exit(1)

    slides = SCRIPT_DIR / "slides.md"

    # Create tmux session with presenterm
    subprocess.run(
        [
            "tmux",
            "new-session",
            "-d",
            "-s",
            SESSION,
            "-x",
            str(os.get_terminal_size().columns),
            "-y",
            str(os.get_terminal_size().lines),
            f"presenterm {slides}",
        ],
        check=True,
    )

    # Propagate environment variables into the tmux session
    for var in os.environ:
        subprocess.run(
            ["tmux", "set-environment", "-t", SESSION, var, os.environ[var]],
            check=False,
        )

    # Advance presenterm to the right slide
    for _ in range(step):
        subprocess.run(
            ["tmux", "send-keys", "-t", f"{SESSION}:0.0", "Right"], check=False
        )
        time.sleep(0.1)

    # Split a claude pane below presenterm (20% height)
    result = subprocess.run(
        [
            "tmux",
            "split-window",
            "-v",
            "-l",
            "20%",
            "-t",
            f"{SESSION}:0.0",
            "-P",
            "-F",
            "#{pane_id}",
            "claude --dangerously-skip-permissions --model haiku",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    claude_pane = result.stdout.strip()

    # Write initial state
    save_state({"step": step, "panes": {"claude": claude_pane}})

    if step > 0:
        print(f"Resuming from step {step}/{len(steps)}: {steps[step - 1]['name']}")

    # Attach
    os.execvp("tmux", ["tmux", "attach", "-t", SESSION])


def cmd_reset() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    print("State reset. Ready for step 1.")


def cmd_status() -> None:
    steps = load_steps()
    state = load_state()
    step_index: int = state["step"]  # type: ignore[assignment]
    panes: dict[str, str] = state.get("panes", {})  # type: ignore[assignment]

    print(f"Step: {step_index}/{len(steps)}")
    if step_index < len(steps):
        step = steps[step_index]
        print(f"Next: {step['name']} -- {step.get('description', '')}")
    else:
        print("Demo complete.")

    if panes:
        print(f"Active panes: {', '.join(panes.keys())}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo step driver")
    parser.add_argument(
        "command",
        choices=["start", "next", "reset", "status"],
        help="Subcommand to run",
    )
    parser.add_argument(
        "step",
        nargs="?",
        type=int,
        default=0,
        help="Step number to resume from (only for start)",
    )
    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args.step)
    elif args.command == "next":
        cmd_next()
    elif args.command == "reset":
        cmd_reset()
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
