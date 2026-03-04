# Vibe Configuring

## Declarative system config with AI

Jonas Chevalier — SF Nix Meetup, March 2026

---

## The problem

- NixOS is great for declarative system configuration
- But not every machine runs NixOS
- Cloud VMs, CI runners, containers — often Ubuntu/Debian
- What if you could use NixOS modules... anywhere?

---

## system-manager

- Nix modules on **any Linux distro**
- Same familiar NixOS options: `services.nginx`, `environment.etc`, `users.users`
- Manages `/etc`, systemd services, users/groups, packages
- One command: `system-manager switch --flake .`
- No NixOS install required — just Nix

---

## What it manages

| Module | What it does |
|--------|-------------|
| `environment.systemPackages` | Install packages |
| `environment.etc.*` | Write files to /etc |
| `services.nginx` | Full nginx config |
| `security.acme` | Let's Encrypt certs |
| `systemd.services.*` | Systemd units |
| `users.users.*` | Declare users |

---

## Vibe configuring

> "Configure my server" → Claude Code edits the Nix config → `nix run .#switch`

- Claude Code reads `CLAUDE.md` to understand the system
- Edits `configuration.nix` like a NixOS config
- Applies changes with one command
- Declarative + AI = vibe configuring

---

## Live demo

1. Fresh Ubuntu 24.04 VM on Hetzner
2. Nix installed, minimal config applied
3. Ask Claude Code to set up something
4. Watch it edit → apply → verify

---

## The setup

```
demo-system-manager/
├── flake.nix              # system-manager + nixpkgs
├── hosts/demo/
│   └── configuration.nix  # the config Claude edits
├── CLAUDE.md              # instructions for Claude Code
└── README.md
```

`CLAUDE.md` tells Claude what modules exist and how to apply.

---

## Why this matters

- **Nix without NixOS** — use Nix modules on any distro
- **AI-friendly** — declarative config is easy for LLMs
- **Reproducible** — it's all in git
- **Fast iteration** — describe what you want, get it

---

## Links

- **Repo:** github.com/zimbatm/demo-system-manager
- **system-manager:** github.com/numtide/system-manager
- **Claude Code:** claude.com/claude-code
- **Numtide:** numtide.com
