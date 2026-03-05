{
  pkgs,
  lib,
  ...
}:
{
  config = {
    nixpkgs.hostPlatform = "x86_64-linux";
    nixpkgs.config.allowUnfreePredicate =
      pkg:
      builtins.elem (pkgs.lib.getName pkg) [
        "claude-code"
      ];

    # Use numtide's binary cache for faster builds
    nix.settings = {
      extra-substituters = [ "https://cache.numtide.com" ];
      extra-trusted-public-keys = [ "niks3.numtide.com-1:DTx8wZduET09hRmMtKdQDxNNthLQETkc/yaX7M4qK0g=" ];
    };

    # System packages
    environment.systemPackages = [
      pkgs.claude-code
      pkgs.ripgrep
      pkgs.htop
    ];

    # Enable userborn for user management
    services.userborn.enable = true;

    # Users
    users.users.demo = {
      isNormalUser = true;
      extraGroups = [ "wheel" ];
    };
    users.groups.wheel.gid = lib.mkForce 900;

    # Allow wheel to sudo without password
    environment.etc."sudoers.d/wheel".text = ''
      %wheel ALL=(ALL:ALL) NOPASSWD: ALL
    '';

    # SSH authorized keys config
    environment.etc."ssh/sshd_config.d/authorized_keys.conf".text = ''
      StrictModes no
      AuthorizedKeysFile .ssh/authorized_keys /etc/ssh/authorized_keys.d/%u
    '';
  };
}
