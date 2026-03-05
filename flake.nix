{
  description = "Vibe-configuring a VM with system-manager + Claude Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    system-manager.url = "github:numtide/system-manager?ref=refs/pull/266/head";
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
      pkgs = import nixpkgs {
        inherit system;
        config.allowUnfreePredicate =
          pkg:
          builtins.elem (pkgs.lib.getName pkg) [
            "claude-code"
          ];
      };
      sm = system-manager.packages.${system}.default;

      switch = pkgs.writeShellScript "switch" ''
        exec ${sm}/bin/system-manager switch --flake ${self} --sudo "$@"
      '';
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.presenterm
          pkgs.hcloud
          pkgs.claude-code
          (pkgs.python3.withPackages (ps: [
            ps.pyyaml
            ps.types-pyyaml
          ]))
          pkgs.ruff
          pkgs.mypy
        ];
      };

      apps.${system} = {
        switch = {
          type = "app";
          program = "${switch}";
        };
        demo =
          let
            demoPython = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
            demoDir = pkgs.runCommand "demo-assets" { } ''
              mkdir -p $out
              cp ${./demo/run-demo.sh} $out/run-demo.sh
              cp ${./demo/demo-steps.py} $out/demo-steps.py
              cp ${./demo/steps.yaml} $out/steps.yaml
              cp ${./demo/slides.md} $out/slides.md
              cp ${./demo/numtide-logo.png} $out/numtide-logo.png
            '';
            runtimePath = pkgs.lib.makeBinPath [
              pkgs.tmux
              pkgs.presenterm
              pkgs.claude-code
              demoPython
              pkgs.coreutils
              pkgs.hcloud
            ];
            wrapper = pkgs.writeShellScript "run-demo" ''
              export PATH="${runtimePath}:$PATH"
              exec ${pkgs.bash}/bin/bash ${demoDir}/run-demo.sh "$@"
            '';
          in
          {
            type = "app";
            program = "${wrapper}";
          };
        demo-only =
          let
            inherit (self.apps.${system}.demo) program;
            wrapper = pkgs.writeShellScript "run-demo-only" ''
              exec ${program} 12
            '';
          in
          {
            type = "app";
            program = "${wrapper}";
          };
        default = self.apps.${system}.demo;
      };

      formatter.${system} =
        (treefmt-nix.lib.evalModule pkgs {
          projectRootFile = "flake.nix";
          programs.nixfmt.enable = true;
        }).config.build.wrapper;

      systemConfigs.default = system-manager.lib.makeSystemConfig {
        modules = [
          ./hosts/demo/configuration.nix
        ];
      };
    };
}
