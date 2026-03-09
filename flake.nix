{
  description = "Vibe-configuring a VM with system-manager + Claude Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
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
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.bashInteractive
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
        demo =
          let
            demoPython = pkgs.python3.withPackages (ps: [ ps.pyyaml ]);
            demoDir = pkgs.runCommand "demo-assets" { } ''
              mkdir -p $out
              cp ${./demo/demo-steps.py} $out/demo-steps.py
              cp ${./demo/steps.yaml} $out/steps.yaml
              cp ${./demo/slides.md} $out/slides.md
              cp ${./demo/numtide-logo.png} $out/numtide-logo.png
              cp ${./demo/CLAUDE.md} $out/CLAUDE.md
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
              exec ${demoPython}/bin/python3 ${demoDir}/demo-steps.py start "$@"
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
    };
}
