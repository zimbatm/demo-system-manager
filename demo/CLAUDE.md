# System Manager Configuration Guide

You are configuring an Ubuntu 24.04 machine using **system-manager** -- a tool that brings NixOS-style declarative configuration to non-NixOS Linux systems with systemd.

## Quick Reference

Configuration file: `~/.config/system-manager/system.nix`

Apply changes:
```bash
nix run 'github:numtide/system-manager' -- switch --sudo
```

Build without activating (dry run):
```bash
nix run 'github:numtide/system-manager' -- build
```

## Architecture

System-manager has two phases:
1. **Build** (unprivileged) -- evaluates Nix modules, builds derivations
2. **Activate** (root via `--sudo`) -- symlinks `/etc` files, installs systemd units, starts services

Managed files live in `/nix/store`. Each activation creates a numbered generation in `/nix/var/nix/profiles/system-manager-profiles/` for rollback.

## flake.nix Structure

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    system-manager = {
      url = "github:numtide/system-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = { nixpkgs, system-manager, ... }: {
    systemConfigs.default = system-manager.lib.makeSystemConfig {
      modules = [ ./system.nix ];
    };
  };
}
```

The entry point is `system-manager.lib.makeSystemConfig { modules = [ ... ]; }`.

## Available Module Options

### nixpkgs (required)

```nix
nixpkgs.hostPlatform = "x86_64-linux";
```

Optional: `nixpkgs.overlays`, `nixpkgs.config` (e.g. `{ allowUnfree = true; }`).

### environment.systemPackages

Installs packages to `/run/system-manager/sw/bin/` (added to PATH via `/etc/profile.d/system-manager-path.sh`).

```nix
environment.systemPackages = with pkgs; [ htop git curl ];
```

### environment.etc

Manages files under `/etc/`. Default mode is `"symlink"` (symlink to Nix store). Set a mode like `"0644"` to copy instead.

```nix
environment.etc."myapp/config.toml" = {
  text = ''
    [server]
    port = 8080
  '';
  # mode = "0644";         # copy instead of symlink
  # uid = 1000;            # owner (only for copies)
  # gid = 1000;            # group (only for copies)
  # user = "myapp";        # takes precedence over uid
  # group = "myapp";       # takes precedence over gid
  # replaceExisting = true; # backup and replace pre-existing files
};
```

Use `replaceExisting = true` when managing files that already exist on the system (e.g. `/etc/nix/nix.conf` created by the Nix installer).

### systemd.services

Services should use `wantedBy = [ "system-manager.target" ]` (not `multi-user.target`). The `system-manager.target` is wanted by `default.target`, so services start on activation and on boot.

```nix
systemd.services.myapp = {
  enable = true;
  description = "My Application";
  wantedBy = [ "system-manager.target" ];
  after = [ "network.target" ];
  serviceConfig = {
    Type = "simple";
    ExecStart = "${pkgs.myapp}/bin/myapp";
    Restart = "always";
    RestartSec = "10s";
    # DynamicUser = true;  # auto-creates ephemeral user, no users.users needed
  };
  # environment = { FOO = "bar"; };
  # script = "...";  # alternative to ExecStart
};
```

### systemd.timers

```nix
systemd.timers.my-timer = {
  wantedBy = [ "timers.target" ];
  timerConfig.OnCalendar = "hourly";  # or "daily", "*:0/5" (every 5 min), etc.
};
systemd.services.my-timer = {
  serviceConfig.Type = "oneshot";
  script = "echo 'timer fired'";
};
```

### systemd.sockets, systemd.paths, systemd.slices, systemd.mounts, systemd.automounts

All standard systemd unit types are supported with the same NixOS-style options.

### systemd.maskedUnits

Mask distro-shipped units by symlinking them to `/dev/null`:

```nix
systemd.maskedUnits = [ "ssh.service" "ModemManager.service" ];
```

### systemd.tmpfiles

Create directories, files, or symlinks via `systemd-tmpfiles`:

```nix
# String format: "type path mode user group age [argument]"
systemd.tmpfiles.rules = [
  "d /var/lib/myapp 0755 myapp myapp -"
  "f /var/log/myapp.log 0644 myapp myapp 30d"
];

# Or structured settings format:
systemd.tmpfiles.settings."10-myapp" = {
  "/var/lib/myapp".d = {
    mode = "0755";
    user = "myapp";
    group = "myapp";
  };
};
```

### users.users and users.groups

User/group management via userborn. `services.userborn.enable` defaults to `true`.

```nix
# System user (for services)
users.users.myapp = {
  isSystemUser = true;
  group = "myapp";
  home = "/var/lib/myapp";
  # createHome = true;
};
users.groups.myapp = {};

# Normal user
users.users.alice = {
  isNormalUser = true;
  description = "Alice";
  home = "/home/alice";
  extraGroups = [ "wheel" ];
  initialPassword = "changeme";  # only set on first creation
  shell = pkgs.bash;
};
```

### services.nginx

Full NixOS nginx module is available. System-manager forces `DynamicUser = true` and `wantedBy = [ "system-manager.target" ]`.

```nix
services.nginx = {
  enable = true;
  virtualHosts."example.com" = {
    root = "/var/www/example";
    # forceSSL = true;
    # enableACME = true;
  };
};
```

The nginx user/group UIDs are forced to 980 by system-manager.

### security.acme (Let's Encrypt)

```nix
security.acme = {
  acceptTerms = true;
  defaults.email = "you@example.com";
};
services.nginx.virtualHosts."example.com" = {
  enableACME = true;
  forceSSL = true;
};
# Required: acme user and group
users.users.acme = { isSystemUser = true; group = "acme"; };
users.groups.acme = {};
```

### nix.settings

Configure the Nix daemon. Remember to set `replaceExisting` since the Nix installer creates `/etc/nix/nix.conf`.

```nix
nix.settings = {
  experimental-features = [ "nix-command" "flakes" ];  # already defaulted
  trusted-users = [ "root" "ubuntu" ];
  substituters = [ "https://cache.numtide.com" ];
  trusted-public-keys = [ "cache.numtide.com-1:..." ];
};
environment.etc."nix/nix.conf".replaceExisting = true;
```

### networking.firewall (stub)

The firewall options exist for NixOS module compatibility but system-manager does NOT manage firewall rules. A warning is emitted if ports are configured. Manage the firewall via the host distro (ufw, iptables, etc.).

### systemd.globalEnvironment

Environment variables passed to all systemd units:

```nix
systemd.globalEnvironment = { TZ = "UTC"; };
```

## What System Manager Does NOT Manage

- **Kernel, bootloader** -- managed by the distro
- **Firewall** -- managed by the distro (options are stubs)
- **Files outside /etc** -- except packages in `/run/system-manager/sw/`
- **Boot-time configuration** -- `boot.*` options are stubs

## Common Pitfalls

- Do NOT delete `/etc/nix` or `/etc/nix/nix.conf` -- it is created by the Nix installer and required for Nix to work. System-manager manages it in place using `replaceExisting = true`, which backs up the original and restores it on deactivation.
- Use `wantedBy = [ "system-manager.target" ]` for services, not `multi-user.target`
- Set `environment.etc."nix/nix.conf".replaceExisting = true` when managing Nix settings
- Declare `users.users` and `users.groups` for any service that needs a dedicated user
- The `acme` user/group must be manually declared when using `security.acme`
- Packages are available at `/run/system-manager/sw/bin/`, not `/usr/bin/`
- After editing, always apply with: `nix run 'github:numtide/system-manager' -- switch --sudo`
