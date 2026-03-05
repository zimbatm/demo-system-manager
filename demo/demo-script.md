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

This launches a tmux session with presenterm on the left and Claude Code on the right. When you advance slides, speaker notes are automatically typed into Claude's pane.

## Manual setup

### 1. Start tmux with two panes

```bash
tmux new-session -s demo \; split-window -h \; select-pane -t 0
```

### 2. Left pane: start presenterm

```bash
presenterm --publish-speaker-notes demo/slides.md
```

### 3. Right pane: start Claude Code

```bash
claude
```

### 4. Start the slide follower (background)

In a separate shell:

```bash
bash demo/slide-follower.sh demo/slides.md demo:0.1 &
```

This listens for presenterm UDP events and types speaker notes directly into Claude's tmux pane.

## Running the demo

1. Advance slides in the left pane with arrow keys
2. Speaker notes are automatically sent to Claude -- no manual interaction needed
3. Some slides are informational (no speaker note) -- nothing is sent

## Timing

- Title + problem + system-manager slides: ~2 min
- Live demo (bootstrap + vibe configure): ~7 min
- Wrap-up: ~1 min
- Total: ~10 minutes

## Prerequisites

- `HCLOUD_TOKEN` environment variable set for Hetzner Cloud API access

## Reset for re-demo

```bash
hcloud server delete demo
```

The next run will create a fresh VM automatically via the speaker notes.
