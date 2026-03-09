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

## Importing NixOS modules

system-manager ships with a curated set (nginx, ACME, userborn, ...) but **~60% of NixOS modules work out of the box**.

```nix
{ nixosModulesPath, ... }:
{
  imports = [
    (nixosModulesPath + "/services/monitoring/prometheus/exporters.nix")
  ];
}
```

Best candidates: modules that only need **systemd units + /etc files + packages**.

Some modules need **stub options** for NixOS-specific deps (`boot.*`, activation scripts).

<!-- end_slide -->

## What it does NOT manage

- **Kernel** — managed by your distro
- **Bootloader** — managed by your distro
- **Distro packages** — apt/dnf/yum are untouched
- **Files outside /etc** — except packages in `/run/`

By design: **coexist peacefully** with apt, manual edits, home-manager.

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
- **Clean uninstall:** `system-manager deactivate --sudo` removes everything

<!-- end_slide -->

## NixOS vs system-manager

| | NixOS | system-manager |
|---|---|---|
| Base system | Nix all the way down | Your distro |
| Kernel | Managed | Distro |
| Package manager | Only Nix | Nix (apt/dnf untouched) |
| `/etc` config | Declarative | Declarative |
| systemd services | Declarative | Declarative |
| Rollback | Full system | Services + packages |
| Migration | All or nothing | Incremental |

<!-- end_slide -->

## Demo time!

Let's try it on a fresh Ubuntu 24.04 VM.

1. Create the VM
2. Install Nix
3. Run `system-manager init`
4. Vibe-configure with Claude Code

<!-- end_slide -->

## Install Nix

```bash
# Install Nix system-wide
curl -sSfL https://artifacts.nixos.org/nix-installer \
  | sh -s -- install --no-confirm
```

<!-- end_slide -->

## system-manager init

```bash
# Generate a starter config
nix run --accept-flake-config \
  'github:numtide/system-manager' -- init

# Edit ~/.config/system-manager/system.nix, then apply
nix run --accept-flake-config \
  'github:numtide/system-manager' -- switch
```

<!-- end_slide -->

## Live vibe configuring

Let's configure the server — by talking to Claude Code.

<!-- end_slide -->

## What we saw

- **system-manager init** — one command to scaffold a config
- **NixOS modules on Ubuntu** — same `services.nginx`, `systemd.services`, ...
- **AI-assisted config** — Claude Code reads and writes declarative Nix naturally
- **Atomic apply** — `switch --sudo` builds, then activates in one step
- **Generations** — every apply is tracked, rollback is one command

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
