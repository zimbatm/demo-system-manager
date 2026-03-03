# Demo: system-manager + Claude Code

You are configuring an Ubuntu 24.04 VM on Hetzner using **system-manager** — a tool that brings NixOS-style declarative configuration to non-NixOS Linux systems.

## How it works

All system configuration lives in `hosts/demo/configuration.nix`. This is a NixOS-style module. You edit it, then apply with:

```bash
nix run .#switch
```

This builds the configuration and activates it on the current machine via `system-manager switch`.

## What you can configure

system-manager supports a subset of NixOS modules:

| Module path | What it does |
|---|---|
| `environment.systemPackages` | Install packages (from `pkgs`) |
| `environment.etc.<name>.text` | Write files to `/etc/` |
| `services.nginx` | Full nginx config with virtualHosts |
| `security.acme` | Let's Encrypt certificates |
| `services.userborn` | User/group management |
| `users.users.<name>` | Declare users |
| `users.groups.<name>` | Declare groups |
| `nix.settings` | Nix daemon configuration |
| `systemd.services.<name>` | Systemd service units |
| `systemd.timers.<name>` | Systemd timers |
| `nixpkgs.hostPlatform` | Target platform (set to `"x86_64-linux"`) |

## Key patterns

### Adding packages
```nix
environment.systemPackages = [
  pkgs.htop
  pkgs.git
  pkgs.nginx
];
```

### Writing config files to /etc
```nix
environment.etc."myapp/config.toml".text = ''
  [server]
  port = 8080
'';
```

### Nginx with ACME
```nix
security.acme = {
  acceptTerms = true;
  defaults.email = "you@example.com";
};

services.nginx = {
  enable = true;
  virtualHosts."example.com" = {
    enableACME = true;
    forceSSL = true;
    root = "/var/www/example";
  };
};
```

For nginx with ACME, you also need an `acme` user and group:
```nix
users.users.acme = { isSystemUser = true; group = "acme"; };
users.groups.acme = {};
users.groups.nginx.gid = lib.mkForce 33993;
```

### Systemd services
```nix
systemd.services.myapp = {
  description = "My Application";
  wantedBy = [ "multi-user.target" ];
  serviceConfig = {
    ExecStart = "${pkgs.myapp}/bin/myapp";
    Restart = "always";
  };
};
```

## Important notes

- The VM is Ubuntu 24.04 — the underlying OS still has apt, systemd, etc. system-manager layers Nix config on top.
- `nixpkgs.hostPlatform` must be `"x86_64-linux"`.
- Always run `nix fmt` before committing.
- After editing `configuration.nix`, apply with `nix run .#switch`.
- If a service needs a dedicated user/group, declare them in `users.users` / `users.groups`.
- `services.userborn.enable = true;` is required for user management to work.
- The `wheel` group GID is forced to 900 to avoid conflicts with Ubuntu's existing groups.
- Nix build users (`nixbld1`-`nixbld32`) are pre-configured — don't remove them.
