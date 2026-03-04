# Demo Script

## Flow

### 1. SSH into fresh VM, show it's plain Ubuntu (~30s)

```bash
ssh root@46.224.195.213
uname -a
cat /etc/os-release | head -3
# → Ubuntu 24.04, plain Linux kernel, no Nix
```

"This is a stock Ubuntu 24.04 VM. No Nix. No NixOS."

### 2. Kick off bootstrap (~15s)

```bash
curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash
```

"This installs Nix and applies our base config. Let it run while I explain."

### 3. Switch to slides (~3-4 min)

Present slides while bootstrap runs in background. The ~5min build time is hidden behind the presentation.

### 4. Come back to the terminal — bootstrap is done

```bash
source /etc/profile.d/system-manager-path.sh
which rg
id demo
# → Nix-managed packages and users on Ubuntu
```

"Nix modules on Ubuntu. No NixOS install."

### 5. Open Claude Code for vibe configuring (~5 min)

```bash
cd demo-system-manager
```

Option A — nginx with a static site:
> "Set up nginx serving a simple welcome page on port 80. Include a nice HTML page."

Option B — full dev environment:
> "Set up a dev environment with git, tmux, neovim, and a welcome message in /etc/motd"

Option C — monitoring stack:
> "Install and configure prometheus-node-exporter as a systemd service"

### 6. Watch Claude work

- Claude reads `CLAUDE.md`, understands the available modules
- Edits `configuration.nix`
- Runs `nix run .#switch`
- Shows the result

### 7. Verify (~30s)

For nginx:
```bash
curl localhost
# → Shows the page
```

For dev env:
```bash
cat /etc/motd
tmux --version
```

## Timing

- Show VM + bootstrap: ~1 min
- Slides (while bootstrap runs): ~4 min
- Vibe configuring demo: ~5 min
- Total: ~10 minutes

## Backup plan

If Claude Code is slow or the network is flaky:
1. Have a pre-recorded terminal session ready (asciinema)
2. Or manually edit the config and run switch yourself, narrating what Claude would do

## Reset for re-demo

```bash
# Destroy and recreate the VM, then bootstrap again:
curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash
```
