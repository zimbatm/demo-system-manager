---
title: system-manager
sub_title: Declarative system config for Linux
author: Jonas Chevalier — Bay Area Nix Meetup @ UC Berkeley OCF, March 2026
---

## The problem

- Many orgs **mandate** Ubuntu/Debian (compliance, vendor support, cloud images)
- Traditional tools are **imperative** — Ansible, Chef, Puppet
  - Configuration drift over time
  - No atomic rollback
  - Hard to reproduce
- NixOS solves all of this... but requires **replacing the entire OS**

<!-- end_slide -->

## The gap

```
  Full NixOS          ???           Ansible/Chef
  ┌──────────┐    ┌────────────┐    ┌──────────────┐
  │ Replace  │    │ Declarative│    │  Imperative  │
  │ whole OS │    │ on any     │    │  scripts on  │
  │ with Nix │    │ distro*    │    │  any distro  │
  └──────────┘    └────────────┘    └──────────────┘
  Reproducible      ???            Config drift
  All or nothing                   Flexible

  * Requires systemd. Tested on Ubuntu, community support
    for Debian, Fedora, Arch.
```

What if you could use NixOS modules **without replacing the OS**?

<!-- end_slide -->

## system-manager

Declarative system configuration for **Linux distros with systemd**.

- Same NixOS module syntax sysadmins already know
- `services.nginx`, `environment.etc`, `systemd.services`, ...
- Coexists with apt/dnf — doesn't replace your distro
- **AI-friendly** — declarative Nix is easy for LLMs to read and write
- One command to apply:

```bash
system-manager switch --flake . --sudo
```

<!-- end_slide -->

## Origin story

- Created by **Numtide** (Ramses / R-VdP) in February 2023
- Grew from a real need: manage non-NixOS servers with Nix
- Think **"Home Manager, but for the whole system"**
- **v1.0.0** released January 2026 — production-ready
- Full docs at **system-manager.net**

<!-- end_slide -->

## How it works

Two phases, two binaries:

```
  ┌────────────────────────┐     ┌────────────────────────┐
  │   1. BUILD (no root)   │     │  2. ACTIVATE (root)    │
  │                        │     │                        │
  │  Nix evaluates modules │────>│  Symlink /etc files    │
  │  Builds all derivations│     │  Start/stop systemd    │
  │  Pure, reproducible    │     │  Apply tmpfiles        │
  │                        │     │  Register generation   │
  └────────────────────────┘     └────────────────────────┘
       system-manager               system-manager-engine
       (unprivileged)               (privileged, via sudo)
```

<!-- end_slide -->

## What it manages

| Component | Where |
|-----------|-------|
| Packages | `/run/system-manager/sw/bin/` |
| `/etc` files | Symlinks from Nix store |
| systemd services | `/etc/systemd/system/` |
| systemd timers, sockets, paths | `/etc/systemd/system/` |
| tmpfiles.d | `/etc/tmpfiles.d/` |
| Users and groups | Via userborn |
| NixOS modules: nginx, ACME | Imported from nixpkgs |
| Nix daemon settings | `/etc/nix/nix.conf` |

<!-- end_slide -->

## What it does NOT manage

- **Kernel** — managed by your distro
- **Bootloader** — managed by your distro
- **Files outside /etc** — except packages in `/run/`

By design: **coexist peacefully** with apt, manual edits, home-manager.

**Clean uninstall:** `system-manager deactivate --sudo` removes all managed
files and stops all managed services — your system goes back to how it was.

<!-- end_slide -->

## Safety model

- **Tracks every file** it manages in a state JSON
- **Refuses to overwrite** unmanaged files
- **Generational profiles** — every activation creates a numbered generation:

```
/nix/var/nix/profiles/system-manager-profiles/
  system-manager-1-link -> /nix/store/...-system
  system-manager-2-link -> /nix/store/...-system
  system-manager         -> system-manager-3-link
```

- Rollback: switch to a previous generation

<!-- end_slide -->

## NixOS vs system-manager

| | NixOS | system-manager |
|---|---|---|
| Base system | Nix all the way down | Your distro |
| Kernel | Managed | Distro |
| Package manager | Only Nix | Nix + apt/dnf |
| `/etc` config | Declarative | Declarative |
| systemd services | Declarative | Declarative |
| Rollback | Full system | Services + packages |
| Migration | All or nothing | Incremental |

<!-- end_slide -->

## Remote deployment

```bash
# Deploy to one machine
system-manager --target-host root@server \
  switch --flake . --sudo

# Deploy to a fleet
for host in "${HOSTS[@]}"; do
  system-manager --target-host "$host" \
    switch --flake . --sudo
done
```

Uses `nix-copy-closure` + SSH. Zero install on the target — just needs Nix.

<!-- end_slide -->

## Getting started

```bash
# Install Nix system-wide
curl -sSfL https://artifacts.nixos.org/nix-installer \
  | sh -s -- install

# Initialize a new config
nix run 'github:numtide/system-manager' -- init

# Edit system.nix, then apply
nix run 'github:numtide/system-manager' -- \
  switch --flake . --sudo
```

<!-- end_slide -->

## Minimal config

```nix
{ pkgs, ... }: {
  nixpkgs.hostPlatform = "x86_64-linux";
  environment.systemPackages = [ pkgs.htop pkgs.ripgrep ];

  services.nginx = {
    enable = true;
    virtualHosts."localhost".root = "/var/www";
  };
}
```

<!-- end_slide -->

## Demo time!

For this demo, we have a pre-built config repo. Let's see it in action:

1. Create an Ubuntu 24.04 VM on Hetzner
2. Bootstrap: install Nix + apply the base config
3. Vibe-configure the machine with Claude Code

<!-- end_slide -->

## SSH & bootstrap

The bootstrap script:

1. Installs Nix via the official installer
2. Clones this repo onto the VM
3. Runs `nix run .#switch` — first system-manager activation

<!-- end_slide -->

## The configuration

- `CLAUDE.md` — teaches Claude Code how to use system-manager
- `hosts/demo/configuration.nix` — the declarative system config

<!-- end_slide -->

## Live vibe configuring

Let's configure the server -- by talking to Claude Code.

<!-- end_slide -->

## Why this matters

- **Nix without NixOS** — use Nix modules on Ubuntu, Debian, Fedora, ...
- **AI-friendly** — declarative config is easy for LLMs to read and write
- **Reproducible** — everything is in git, every change is a generation
- **Incremental adoption** — start with one service, expand over time
- **Production-ready** — v1.0.0, full docs, commercial support from Numtide

<!-- end_slide -->

## Links

![](numtide-logo.png)

- **Docs:** system-manager.net
- **Repo:** github.com/numtide/system-manager
- **This demo:** github.com/zimbatm/demo-system-manager
- **Claude Code:** claude.ai/code
- **Numtide:** numtide.com

<!-- end_slide -->

## Thanks!
