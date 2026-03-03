{
  pkgs,
  lib,
  ...
}:
{
  config = {
    nixpkgs.hostPlatform = "x86_64-linux";

    # Nix configuration
    nix.settings = {
      experimental-features = lib.mkDefault [
        "nix-command"
        "flakes"
      ];
    };

    # System packages
    environment.systemPackages = [
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

    # Nix build users
    users.users = lib.genAttrs (builtins.map (n: "nixbld${toString n}") (lib.range 1 32)) (name: {
      isSystemUser = true;
      group = "nixbld";
      uid = 30000 + lib.toInt (lib.removePrefix "nixbld" name);
    });
    users.groups.wheel.gid = lib.mkForce 900;
    users.groups.nixbld = {
      gid = 30000;
      members = builtins.map (n: "nixbld${toString n}") (lib.range 1 32);
    };

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
