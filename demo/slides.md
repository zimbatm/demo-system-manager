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

<!-- end_slide -->

## system-manager

- Nix modules on **any Linux distro**
- Same familiar NixOS options: `services.nginx`, `environment.etc`, `users.users`
- Manages `/etc`, systemd services, users/groups, packages
- One command: `system-manager switch --flake .`
- No NixOS install required — just Nix

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

<!-- end_slide -->

## Vibe configuring

> "Configure my server" -> Claude Code edits the Nix config -> `nix run .#switch`

- Claude Code reads `CLAUDE.md` to understand the system
- Edits `configuration.nix` like a NixOS config
- Applies changes with one command
- Declarative + AI = vibe configuring

<!-- end_slide -->

## Live demo

1. SSH into a fresh Ubuntu 24.04 VM
2. Bootstrap: install Nix + base config
3. Come back when it's done
4. Vibe configure with Claude Code

<!-- speaker_note: "SSH into the demo VM and show it's plain Ubuntu. Run uname -a and cat /etc/os-release | head -3 to prove there's no Nix installed yet." -->

<!-- end_slide -->

## Bootstrap

```
curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash
```

Installs Nix and applies the base system-manager config.

Takes ~4 minutes to build.

<!-- speaker_note: "Run the bootstrap script on the VM. Then come back to the slides while it builds." -->

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

<!-- end_slide -->

## Bootstrap done!

Let's verify the system is configured:

- Nix-managed packages available
- Users and groups created
- system-manager active

<!-- speaker_note: "Check that bootstrap completed. Run source /etc/profile.d/system-manager-path.sh && which rg && id demo to show Nix-managed packages and users are working on Ubuntu." -->

<!-- end_slide -->

## Vibe configure: nginx

Let's ask Claude to set up nginx with a welcome page.

> "Set up nginx serving a welcome page on port 80 with a nice HTML page"

<!-- speaker_note: "Edit configuration.nix to add nginx serving a simple welcome page on port 80. Add a nice HTML page as the root. Include the acme user/group and nginx group as documented in CLAUDE.md. Then apply with nix run .#switch." -->

<!-- end_slide -->

## Verify nginx

```bash
curl localhost
```

<!-- speaker_note: "Verify nginx is working by running curl localhost on the VM. Show the HTML output." -->

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
