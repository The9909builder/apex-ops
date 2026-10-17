#!/usr/bin/env bash
# autovibe — precompile-gate.sh  (v1.0.0 — BACK-COMPAT SHIM)
# ─────────────────────────────────────────────────────────────────────────────
# v0.8.0 made the gate the architecture, not a flag: the (then 7) ULTRA checks
# moved into autovibe-gate.sh's `ultra` mode VERBATIM. v1.0.0 added checks 8-10
# (Phase-0 ordering invariant) there. This shim preserves every existing call
# site — `precompile-gate.sh --ultra <path> [--report <p>]` in ultra.md /
# skill.yaml keeps working, now routed through the one engine (now 10 checks).
#
# Prefer calling `autovibe-gate.sh ultra ...` directly in new code.
# ─────────────────────────────────────────────────────────────────────────────
exec "$(dirname "${BASH_SOURCE[0]}")/autovibe-gate.sh" ultra "$@"
