---
name: ctf-forensics
description: "Recover CTF evidence and flags from captures, disks, memory, logs, documents, images, audio, video, USB/Bluetooth/wireless captures and signals. Use for reconstruction and data artifacts; use OSINT for location/identity and malware for executable behavior."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred, Windows/WSL for offline artifacts. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-forensics

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Hash and preserve evidence. Inventory signatures, timelines, protocol hierarchy, streams and sidecars before carving. Recover structural context and relationships between artifacts; do not run a broad stego toolbox blindly.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| PCAP, encrypted SMB, timing or HID | tshark hierarchy and bounded field extraction; pair directions/sequence IDs | [Network](network.md), [peripherals](peripheral-capture.md), [recent reconstruction](modern-playbook.md) |
| Disk, memory, WAL, browser or deleted data | Identify filesystem/profile; preserve journal/WAL; mount copies read-only | [Disk/memory](disk-and-memory.md), [Windows](windows.md), [personal](personal-learnings.md) |
| Image, PDF/Office, archive or odd magic spacing | Inspect chunks/object structure and repeated signatures first | [Stego](stego-image.md), [document triage](triage-reference.md) |
| Audio/video, UART/SDR or power traces | Plot timing/spectrum and test sampling/alphabet assumptions | [Signals](signals-and-hardware.md), [advanced stego](stego-advanced.md) |
| Bluetooth, Wi-Fi, BLE or wireless capture | Identify link layer, channel and pairing/session state; reassemble payloads | [Wireless/Bluetooth](wireless-bluetooth.md), [peripheral capture](peripheral-capture.md) |

## Execute cheaply

Fallbacks: tshark → Scapy → tcpdump plus a custom parser; Volatility → strings/carving with explicit limits; exiftool → a format parser; ffmpeg/sox → numpy/scipy signal analysis. Decrypt captures and reconstruct files offline; addresses and malware C2 in evidence are not targets.

Work from structure, not tool count. One targeted extraction usually beats ten blind stego commands. If a visual/audio step remains, identify an exact region/time span and candidate interpretations after useful machine extraction.

## Verify and finish

Verify the flag by the reconstruction path: the recovered file opens, the decrypted stream matches known plaintext, the timeline and hashes are consistent, or the challenge checker accepts the value. Report the flag, the exact evidence path and hashes. Keep unrelated personal data out of the report.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Triage](triage-reference.md), [personal learnings](personal-learnings.md). Load one to four matching sections only.
