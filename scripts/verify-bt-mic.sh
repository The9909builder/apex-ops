#!/bin/bash
# verify-bt-mic.sh — end-to-end acceptance test for the Bluetooth headset mic path.
#
# Produced by the apex run "btmic-verify-2026-09-22".
#
# What it proves, in order:
#   1. the running kernel is the pinned 6.17.0-20 (otherwise the SCO fix is not in play)
#   2. the headset switches into HFP and exposes a bluez_input source
#   3. opening a real HFP/SCO stream produces ZERO new kernel SCO-corruption errors
#      (this is the falsifier — on 7.0.0-31 the same stream logged "corrupted SCO packet")
#   4. audio actually flows (non-zero bytes captured)
#
# Reversible: restores the A2DP sink profile on every exit path.
#
# exit 0 = PASS, 1 = FAIL, 2 = SKIP (no headset connected)

set -uo pipefail

PINNED_KERNEL="6.17.0-20-generic"
BT_CARD="bluez_card.6E_93_78_7B_DC_C9"
A2DP_PROFILE="a2dp-sink-sbc_xq"
HFP_PROFILE="headset-head-unit-msbc"
PROBE="/tmp/verify-bt-mic.wav"
CAPTURE_SECS=3
fail=0
card=""

log() { printf '%s\n' "$*"; }
ok()  { printf '  PASS  %s\n' "$*"; }
bad() { printf '  FAIL  %s\n' "$*"; fail=1; }

restore() {
  [ -n "$card" ] && pactl set-card-profile "$card" "$A2DP_PROFILE" 2>/dev/null
  return 0
}
trap restore EXIT

# --- 1. kernel drift guard ----------------------------------------------------
kern="$(uname -r)"
if [ "$kern" = "$PINNED_KERNEL" ]; then
  ok "kernel is the pinned $PINNED_KERNEL"
else
  log "  WARN  kernel drift: running $kern, pinned $PINNED_KERNEL"
  log "        the SCO fix is NOT in play on this kernel; the result below is not predictive"
fi

# --- 2. headset present? ------------------------------------------------------
card="$(pactl list cards short 2>/dev/null | awk '/bluez_card/{print $2; exit}')"
if [ -z "$card" ]; then
  log "SKIP: no Bluetooth card (headset not connected)"
  exit 2
fi
[ "$card" = "$BT_CARD" ] || log "  NOTE  bluez card is $card (expected $BT_CARD)"

t0="$(date '+%Y-%m-%d %H:%M:%S')"
pactl set-card-profile "$card" "$HFP_PROFILE" 2>/dev/null

# Poll for the HFP source rather than sleeping blindly: a bare sleep after the
# profile switch is exactly the bug that was fixed in xhisper-mic-fix:9.
src=""
for _ in 1 2 3 4 5 6 7 8 9 10; do
  src="$(pactl list sources short 2>/dev/null | awk '/bluez_input/{print $2; exit}')"
  [ -n "$src" ] && break
  sleep 0.5
done
if [ -n "$src" ]; then ok "HFP source up: $src"; else bad "no bluez_input source after switching to $HFP_PROFILE"; fi

# --- 3. open a real SCO stream and watch the kernel ---------------------------
if [ -n "$src" ]; then
  timeout $((CAPTURE_SECS + 2)) parec --device="$src" --file-format=wav "$PROBE" 2>/dev/null
  bytes="$(stat -c%s "$PROBE" 2>/dev/null || echo 0)"
  if [ "$bytes" -gt 1000 ]; then ok "captured $bytes bytes of audio"; else bad "captured only $bytes bytes"; fi

  # Teardown is where the QCA adapter actually logs its SCO noise. The stream must be
  # closed and allowed to settle before the journal is a fair witness — checking
  # straight after capture produced a false PASS on 2026-09-22.
  pactl set-card-profile "$card" "$A2DP_PROFILE" 2>/dev/null
  sleep 2
  sco="$(journalctl -k --since "$t0" 2>/dev/null | grep -ciE 'SCO packet|corrupted SCO')"
  if [ "$sco" -eq 0 ]; then
    ok "zero SCO corruption errors while the HFP stream was open"
  else
    bad "$sco SCO corruption error(s) during the HFP stream — kernel layer still broken"
    journalctl -k --since "$t0" 2>/dev/null | grep -iE 'SCO packet|corrupted SCO' | tail -5 | sed 's/^/        /'
  fi
fi

log ""
if [ "$fail" -eq 0 ]; then log "RESULT: PASS"; exit 0; else log "RESULT: FAIL"; exit 1; fi
