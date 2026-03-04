{
  description = "Vibe-configuring a VM with system-manager + Claude Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    system-manager.url = "github:numtide/system-manager?ref=refs/pull/266/head";
    system-manager.inputs.nixpkgs.follows = "nixpkgs";
    system-manager.inputs.userborn.inputs.nixpkgs.follows = "nixpkgs";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      system-manager,
      treefmt-nix,
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      sm = system-manager.packages.${system}.default;

      switch = pkgs.writeShellScript "switch" ''
        exec ${sm}/bin/system-manager switch --flake ${self} --sudo "$@"
      '';
    in
    {
      apps.${system} = {
        switch = {
          type = "app";
          program = "${switch}";
        };
        default = self.apps.${system}.switch;
      };

      formatter.${system} =
        (treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.nixfmt.enable = true;
        }).config.build.wrapper;

      systemConfigs.demo = system-manager.lib.makeSystemConfig {
        modules = [
          ./hosts/demo/configuration.nix
        ];
      };
    };
}
