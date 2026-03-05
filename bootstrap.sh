#!/usr/bin/env bash
set -euo pipefail

# Install Nix
curl -sSfL https://artifacts.nixos.org/nix-installer | sh -s -- install --no-confirm
. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh

# Remove nix-installer's /etc/nix so system-manager can manage it
rm -rf /etc/nix

# Clone the config repo
nix --extra-experimental-features 'nix-command flakes' \
  --extra-substituters https://cache.numtide.com \
  --extra-trusted-public-keys 'niks3.numtide.com-1:DTx8wZduET09hRmMtKdQDxNNthLQETkc/yaX7M4qK0g=' \
  run nixpkgs#git -- \
  clone https://github.com/zimbatm/demo-system-manager.git
cd demo-system-manager

# Apply the base configuration
nix --extra-experimental-features 'nix-command flakes' \
  --extra-substituters https://cache.numtide.com \
  --extra-trusted-public-keys 'niks3.numtide.com-1:DTx8wZduET09hRmMtKdQDxNNthLQETkc/yaX7M4qK0g=' \
  run .#switch
