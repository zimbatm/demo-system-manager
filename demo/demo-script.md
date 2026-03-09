# Demo Script

## Prerequisites

Enter the dev shell to get all required tools:

```bash
nix develop
```

This provides: presenterm, hcloud, claude-code, python3 (with pyyaml), ruff, mypy.

Environment variables needed:

- `HCLOUD_TOKEN` -- Hetzner Cloud API access
- `ANTHROPIC_API_KEY` -- Claude Code

## Quick start

```bash
nix run
```

This launches a tmux session with presenterm showing the slides.

## Presentation structure

### Part 1: system-manager talk (slides 1-12)

Pure presentation, no automation. Just `/next` to advance through:

1. **the-problem** -- Config drift, imperative tools
2. **the-gap** -- The space between NixOS and Ansible
3. **system-manager** -- What it is
4. **origin-story** -- Numtide, Ramses, v1.0.0
5. **how-it-works** -- Build + activate architecture
6. **what-it-manages** -- Packages, /etc, systemd, nginx
7. **what-it-does-not-manage** -- Kernel, bootloader, files outside /etc
8. **safety-model** -- State tracking, generations
9. **nixos-comparison** -- NixOS vs system-manager table
10. **remote-deployment** -- SSH deployment, fleet management
11. **getting-started** -- nix run + init
12. **minimal-config** -- Example system.nix with nginx

### Part 2: live demo (slides 13-19)

13. **demo-time** -- Opens bash pane, creates Hetzner VM
14. **ssh-bootstrap** -- SSHs into VM, runs bootstrap script
15. **the-configuration** -- Shows CLAUDE.md and configuration.nix
16. **live-vibe-configuring** -- Presenter takes over for manual demo
17. **why-this-matters** -- Exits SSH, wrap-up slide
18. **links** -- Deletes VM
19. **thanks** -- Kills tmux session

## Running the demo

1. Start with `nix run`
2. Type `/next` to advance each slide
3. For Part 1, each `/next` just advances the slide -- talk freely
4. At "demo-time", automation kicks in -- bash pane opens, VM is created
5. At "live-vibe-configuring", SSH session is open -- launch Claude Code manually
6. When done demoing, `/next` through the wrap-up slides

## Slash commands

| Command | What it does |
|---------|-------------|
| `/next` | Advance one slide, execute directives |

## Reset for re-demo

Just run `nix run` again -- state resets automatically on start. If the VM is still running:

```bash
hcloud server delete demo
```
