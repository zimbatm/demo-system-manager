Start demo mode. You are being driven by a live presentation:

- A `demo/slide-follower.sh` script runs in the background, listening to presenterm's UDP events.
- It writes the current slide's speaker note to `.current-note`.
- When the user says "next", re-read `.current-note` and execute the instruction it contains.
- Speaker notes contain instructions like "SSH into the VM and run uname -a" or "Edit configuration.nix to add nginx".
- Execute the instruction and briefly narrate what you're doing.
- Some slides are informational (no speaker note) — if `.current-note` hasn't changed, tell the user and wait for "next" again.
- The system-manager configuration docs in CLAUDE.md still apply — use them when speaker notes reference configuring services.
