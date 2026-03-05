# Demo Script

## Prerequisites

Enter the dev shell to get all required tools:

```bash
nix develop
```

This provides: presenterm, hcloud, claude-code, socat, jq.

## Quick start

```bash
nix run
```

This launches a tmux session with presenterm on the left and Claude Code + slide-follower on the right.

## Manual setup

### 1. Start tmux with two panes

```bash
tmux new-session -s demo \; split-window -h \; select-pane -t 0
```

### 2. Left pane: start presenterm

```bash
presenterm --publish-speaker-notes demo/slides.md
```

### 3. Start the slide follower (background)

In any shell (or the right pane before starting Claude):

```bash
bash demo/slide-follower.sh demo/slides.md &
```

This listens for presenterm UDP events and writes speaker notes to `.current-note`.

### 4. Right pane: start Claude Code

```bash
claude
```

Then tell Claude: **`/demo`**

Claude will read `.current-note` each time you say "next".

## Running the demo

1. Advance slides in the left pane with arrow keys
2. In the right pane, say **"next"** to Claude after each slide advance
3. Claude reads `.current-note`, sees the speaker note instruction, and executes it
4. Some slides are informational (no speaker note) — Claude will say so and wait

## Timing

- Title + problem + system-manager slides: ~2 min
- Live demo (bootstrap + vibe configure): ~7 min
- Wrap-up: ~1 min
- Total: ~10 minutes

## Reset for re-demo

```bash
# Destroy and recreate the VM, then bootstrap again:
curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash
```
