{
  pkgs,
  lib,
  ...
}:
{
  config = {
    nixpkgs.hostPlatform = "x86_64-linux";

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
