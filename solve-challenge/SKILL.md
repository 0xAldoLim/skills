---
name: solve-challenge
description: "Triage a CTF challenge, choose its primary and secondary category from evidence, and execute until the flag is verified. Use when the category is unknown or hybrid; use a category skill directly when its primitive is clear."
license: MIT
compatibility: Codex CLI on Kali Linux; local artifacts and optionally an assigned instance.
metadata:
  user-invocable: "true"
---

# Solve the challenge

Read the challenge description, format and attachments. Inventory the challenge directory, hidden files, signatures and sizes. Preserve originals; extract into output/ and keep solver scripts/state in solve/. Search obvious candidates before heavyweight analysis. Establish the exact assigned instance from the user's description; never detect, probe or enumerate a CTF platform as a recon step.

Competition infrastructure (CTFd, scoreboard, submission API, provisioning, organizer networks, shared hosts/nodes, other teams and adjacent IPs) is out of scope. The supplied challenge instance may be tested with justified enumeration, fuzzing, bounded brute force and exploitation. Reachability does not add targets. Stop at the shared infrastructure boundary; if an intended escape reaches an ambiguous next layer, ask about that exact boundary. Read [scope](../docs/SCOPE.md) for remote/escape work.

Before deep remote work, perform a cheap DNS/TCP/TLS and baseline HTTP or protocol check. Generic 404/410/proxy 502/503/504, NXDOMAIN, refused connections and timeouts may mean expiry. Use only a small number of known-route/protocol confirmations; one status code is not proof. If likely expired/unavailable, stop remote exploitation, request refresh, and preserve STATE.md, payloads, offsets and local conclusions. After refresh, update scope, recheck health and replay the existing solver. See [health](../docs/INSTANCE_HEALTH.md).

## Route from evidence, then execute

| Evidence / decisive blocker | Primary skill | Common secondary |
|---|---|---|
| Native behavior/validation, ELF/PE/APK/WASM/custom VM | [$ctf-reverse](../ctf-reverse/SKILL.md) | crypto; pwn after a real primitive |
| Confirmed memory corruption, ROP/format/allocator/kernel primitive | [$ctf-pwn](../ctf-pwn/SKILL.md) | reverse, kernel runtime analysis |
| Equations, encryption, oracle, nonce/PRNG, signatures or PQC | [$ctf-crypto](../ctf-crypto/SKILL.md) | reverse, web |
| HTTP app/API/auth/browser/server parser boundary | [$ctf-web](../ctf-web/SKILL.md) | crypto, reverse, AI/ML |
| Packets, disk/memory/log/document/media reconstruction | [$ctf-forensics](../ctf-forensics/SKILL.md) | crypto, OSINT, signal processing |
| Malicious loader, C2/config/obfuscated package | [$ctf-malware](../ctf-malware/SKILL.md) | reverse, forensics |
| Location, public identity/history, metadata provenance | [$ctf-osint](../ctf-osint/SKILL.md) | forensics |
| Model weights, gradients, tool-using chatbot or tokenization | [$ctf-ai-ml](../ctf-ai-ml/SKILL.md) | web, reverse |
| Jails, Unicode, RF, games, SMT, strange runtime/protocol | [$ctf-misc](../ctf-misc/SKILL.md) | crypto, blockchain/web |

Native artifact plus a port is only a candidate pwn route: first understand the binary. Magic bytes and runtime behavior outrank extensions. `../scripts/triage_artifacts.py` inventories without executing, and `../scripts/classify_challenge.py` provides a heuristic starting route; inspect its evidence rather than treating the score as truth.

Invoke/read the selected category skill, its INDEX.md and one to four matching references; then run the solve, not just the classification. Start with up to three evidence-backed hypotheses and cheap discriminators. Pivot when observations contradict assumptions. Pair artifacts and inspect wrapper/nested payloads before spending heavily on a flashy centerpiece; see [personal learnings](personal-learnings.md).

Use fast mode for obvious paths, normal mode for standard problems, and automatically escalate depth for zero solves, custom implementations, high difficulty or repeated strong failures. Increase local math/reverse/emulation/experiments and technical research, not target scope. Search concepts and analogous vulnerabilities; do not retrieve exact active challenge solutions. Preserve hard-solve state and continue while a meaningful feasible path remains. [Workflow](../docs/WORKFLOW.md) defines handoffs and blocker reports.

## Verify, report, capture

Verify the flag by its derivation, intended artifact or actual checker; format alone is insufficient. Return flag, verification, short path and important solve artifacts. A full polished writeup is only for an explicit [$ctf-writeup](../ctf-writeup/SKILL.md) request. Do not submit to platform APIs automatically.

Automatically capture novel, reproducible, understood techniques after verified successful solves via `../scripts/capture_learning.py --auto`; [learning](../docs/LEARNING.md) explains duplicate/variant checks and promotion. Reject flags, passwords, ephemeral targets, speculative or accidental methods. Never auto-push.
