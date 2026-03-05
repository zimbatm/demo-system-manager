#!/usr/bin/env bash
# Launch the demo: presenterm + Claude Code in tmux.
# Usage: run-demo.sh [step] -- resume from a specific step number
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${script_dir}/demo-steps.py" start "$@"
