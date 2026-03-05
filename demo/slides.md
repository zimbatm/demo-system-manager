---
title: Vibe Configuring
sub_title: Declarative system config with AI
author: Jonas Chevalier — SF Nix Meetup, March 2026
---

<!-- end_slide -->

## The problem

- NixOS is great for declarative system configuration
- But not every machine runs NixOS
- Cloud VMs, CI runners, containers — often Ubuntu/Debian
- What if you could use NixOS modules... anywhere?

<!-- speaker_note: Create a Hetzner VM named 'demo' using hcloud with Ubuntu 24.04, server type cx22, location fsn1. Show the IP address when done. -->

<!-- end_slide -->

## system-manager

- Nix modules on **any Linux distro**
- Same familiar NixOS options: `services.nginx`, `environment.etc`, `users.users`
- Manages `/etc`, systemd services, users/groups, packages
- One command: `system-manager switch --flake .`
- No NixOS install required — just Nix

<!-- speaker_note: SSH into the demo VM and run `uname -a` and `cat /etc/os-release | head -3` to show it's a plain Ubuntu system with no Nix installed. -->

<!-- end_slide -->

## What it manages

| Module | What it does |
|--------|-------------|
| `environment.systemPackages` | Install packages |
| `environment.etc.*` | Write files to /etc |
| `services.nginx` | Full nginx config |
| `security.acme` | Let's Encrypt certs |
| `systemd.services.*` | Systemd units |
| `users.users.*` | Declare users |

<!-- speaker_note: SSH into the demo VM and run `curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash` to install Nix and apply the base config. This takes a few minutes — just kick it off, no need to wait for it to finish. -->

<!-- end_slide -->

## Vibe configuring

> "Configure my server" -> Claude Code edits the Nix config -> `nix run .#switch`

- Claude Code reads `CLAUDE.md` to understand the system
- Edits `configuration.nix` like a NixOS config
- Applies changes with one command
- Declarative + AI = vibe configuring

<!-- speaker_note: SSH into the demo VM and run `cat /root/demo-system-manager/CLAUDE.md` to show the instructions Claude uses to understand the system. -->

<!-- end_slide -->

## The setup

```
demo-system-manager/
├── flake.nix              # system-manager + nixpkgs
├── hosts/demo/
│   └── configuration.nix  # the config Claude edits
├── CLAUDE.md              # instructions for Claude Code
└── demo/
    └── slides.md          # this presentation
```

`CLAUDE.md` tells Claude what modules exist and how to apply.

<!-- speaker_note: SSH into the demo VM and run `cat /root/demo-system-manager/hosts/demo/configuration.nix` to show the current system configuration. -->

<!-- end_slide -->

## Bootstrap done!

Let's verify the system is configured:

- Nix-managed packages available
- Users and groups created
- system-manager active

<!-- speaker_note: SSH into the demo VM and run `source /etc/profile.d/system-manager-path.sh && which rg && id demo` to verify that Nix-managed packages and users are working on Ubuntu. -->

<!-- end_slide -->

## Vibe configure: nginx

Let's ask Claude to set up nginx with a welcome page.

> "Set up nginx serving a welcome page on port 80 with a nice HTML page"

<!-- speaker_note: SSH into the demo VM, cd to demo-system-manager, and edit hosts/demo/configuration.nix to add nginx serving a welcome page on port 80. Write a nice HTML page as the root. Include the acme user/group and nginx group as documented in CLAUDE.md. Then run `nix run .#switch` on the VM to apply. -->

<!-- end_slide -->

## Verify nginx

```bash
curl localhost
```

<!-- speaker_note: SSH into the demo VM and run `curl localhost` to verify nginx is serving the welcome page. -->

<!-- end_slide -->

## Why this matters

- **Nix without NixOS** — use Nix modules on any distro
- **AI-friendly** — declarative config is easy for LLMs
- **Reproducible** — it's all in git
- **Fast iteration** — describe what you want, get it

<!-- end_slide -->

## Links

![](numtide-logo.png)

- **Repo:** github.com/zimbatm/demo-system-manager
- **system-manager:** github.com/numtide/system-manager
- **Claude Code:** claude.com/claude-code
- **Numtide:** numtide.com

<!-- speaker_note: Destroy the demo VM by running `hcloud server delete --poll demo`. Say goodbye to the VM. -->
