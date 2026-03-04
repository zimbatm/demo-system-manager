# Demo Script

## Bootstrap (one-time setup)

```bash
# Install Nix
curl -sSfL https://artifacts.nixos.org/nix-installer | sh -s -- install
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

# Remove nix-installer's /etc/nix so system-manager can manage it
rm -rf /etc/nix

# Clone and apply
git clone https://github.com/zimbatm/demo-system-manager.git
cd demo-system-manager
nix --extra-experimental-features 'nix-command flakes' run .#switch
# After this first run, nix.conf is managed and flakes work natively
```

## Pre-demo checklist

- [ ] VM running: `ssh root@46.224.195.213`
- [ ] Repo cloned on VM: `/root/demo-system-manager`
- [ ] system-manager already applied (base config)
- [ ] Terminal font large enough for audience
- [ ] Claude Code installed and authenticated

## Flow

### 1. Show the VM (30 seconds)

```bash
ssh root@46.224.195.213
uname -a
cat /etc/os-release | head -3
# → Ubuntu 24.04, plain Linux kernel
```

### 2. Show the config (30 seconds)

```bash
cat hosts/demo/configuration.nix
# → Minimal: just packages, users, basic etc files
cat CLAUDE.md
# → Quick scroll: this is what Claude knows about system-manager
```

### 3. Open Claude Code and ask it to configure something (the vibe part)

Option A — nginx with a static site:
> "Set up nginx serving a simple welcome page on port 80. Include a nice HTML page."

Option B — full dev environment:
> "Set up a dev environment with git, tmux, neovim, and a welcome message in /etc/motd"

Option C — monitoring stack:
> "Install and configure prometheus-node-exporter as a systemd service"

### 4. Watch Claude work

- Claude reads `CLAUDE.md`, understands the available modules
- Edits `configuration.nix`
- Runs `nix run .#switch`
- Shows the result

### 5. Verify (30 seconds)

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

- Slides: ~3 minutes
- Demo: ~5 minutes
- Total: ~8 minutes

## Backup plan

If Claude Code is slow or the network is flaky:
1. Have a pre-recorded terminal session ready (asciinema)
2. Or manually edit the config and run switch yourself, narrating what Claude would do

## Reset for re-demo

```bash
# On the VM, revert to base config:
cd /root/demo-system-manager
git checkout main -- hosts/demo/configuration.nix
nix run .#switch
```
