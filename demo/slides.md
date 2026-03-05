---
title: Vibe Configuring
sub_title: Declarative system config with AI
author: Jonas Chevalier — SF Nix Meetup, March 2026
---

## The problem

- Many environments mandate Ubuntu/Debian (compliance, vendor support, cloud images)
- Ansible/Chef/Puppet are imperative — no atomic rollback, hard to reproduce
- NixOS solves this but requires replacing the entire OS

<!-- speaker_note:
pane claude claude --dangerously-skip-permissions
wait 3
type claude Create a Hetzner VM named 'demo' using hcloud with Ubuntu 24.04, server type cpx22, location nbg1. List my SSH keys with hcloud ssh-key list and pass all of them with --ssh-key flags. Show the IP address when done.
-->

<!-- end_slide -->

## system-manager

- Nix modules on **any Linux distro**
- Same familiar NixOS options: `services.nginx`, `environment.etc`, `users.users`
- Manages `/etc`, systemd services, users/groups, packages
- One command: `system-manager switch --flake .`
- No NixOS install required — just Nix

<!-- speaker_note:
pane ssh ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes root@$(hcloud server ip demo)
wait 3
type ssh uname -a
type ssh cat /etc/os-release | head -3
-->

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

<!-- speaker_note:
type ssh curl -sL https://raw.githubusercontent.com/zimbatm/demo-system-manager/main/bootstrap.sh | bash
-->

<!-- end_slide -->

## Vibe configuring

> "Configure my server" -> Claude Code edits the Nix config -> `nix run .#switch`

- Claude Code reads `CLAUDE.md` to understand the system
- Edits `configuration.nix` like a NixOS config
- Applies changes with one command
- Declarative + AI = vibe configuring

<!-- speaker_note:
type ssh cat /root/demo-system-manager/CLAUDE.md
-->

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

<!-- speaker_note:
type ssh cat /root/demo-system-manager/hosts/demo/configuration.nix
-->

<!-- end_slide -->

## Bootstrap done!

Let's verify the system is configured:

- Nix-managed packages available
- Users and groups created
- system-manager active

<!-- speaker_note:
type ssh source /etc/profile.d/system-manager-path.sh && which rg && id demo
-->

<!-- end_slide -->

## Vibe configure: nginx

Let's ask Claude to set up nginx with a welcome page.

> "Set up nginx serving a welcome page on port 80 with a nice HTML page"

<!-- speaker_note:
close ssh
pane server-claude ssh -t -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes root@$(hcloud server ip demo) "cd /root/demo-system-manager && ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY claude --dangerously-skip-permissions"
wait 3
type server-claude Set up nginx serving a welcome page on port 80 with a nice HTML page. Include the acme user/group and nginx group as documented in CLAUDE.md. Then run nix run .#switch to apply.
-->

<!-- end_slide -->

## Verify nginx

```bash
curl localhost
```

<!-- speaker_note:
close server-claude
pane ssh ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes root@$(hcloud server ip demo)
wait 3
type ssh curl localhost
-->

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

<!-- speaker_note:
close ssh
type claude Delete the demo VM by running hcloud server delete demo. Say goodbye to the VM.
-->

<!-- end_slide -->

## Thanks!

<!-- speaker_note:
kill
-->
