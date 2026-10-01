---
name: ctf-forensics
description: "Recover CTF evidence and flags from captures, disks, memory, logs, documents, images and signals. Use for reconstruction and data artifacts; use OSINT for location/identity and malware for executable behavior."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-forensics

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Hash and preserve evidence. Inventory signatures, timelines, protocol hierarchy, streams and sidecars before carving. Recover structural context and relationships between artifacts; do not run a broad stego toolbox blindly.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| PCAP, encrypted SMB, timing or HID | tshark hierarchy and bounded field extraction; pair directions/sequence IDs | [Network](network.md), [peripherals](peripheral-capture.md), [recent reconstruction](modern-playbook.md) |
| Disk, memory, WAL, browser or deleted data | Identify filesystem/profile; preserve journal/WAL; mount copies read-only | [Disk/memory](disk-and-memory.md), [Windows](windows.md), [personal](personal-learnings.md) |
| Image, PDF/Office, archive or odd magic spacing | Inspect chunks/object structure and repeated signatures first | [Stego](stego-image.md), [document triage](triage-reference.md) |
| Audio/video, UART/SDR or power traces | Plot timing/spectrum and test sampling/alphabet assumptions | [Signals](signals-and-hardware.md), [advanced stego](stego-advanced.md) |

Fallbacks: tshark -> Scapy -> tcpdump plus custom parser; Volatility -> strings/carving with explicit limits; exiftool -> format parser; ffmpeg/sox -> numpy/scipy signal analysis. Decrypt captures and reconstruct files offline; addresses and malware C2 in evidence are not targets. A visual/audio handoff must identify an exact region/time span and candidate interpretations after useful machine extraction.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
