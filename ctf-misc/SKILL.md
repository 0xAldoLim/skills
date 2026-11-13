---
name: ctf-misc
description: "Solve CTF jails, unusual encodings, invented languages, esolangs, games, custom games/VMs, RF/SDR, QR/audio, strange formats, protocol puzzles and constraints that do not fit a clearer category. Use as a cross-category fallback; pivot when a specialized primitive becomes dominant."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-misc

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Use evidence to narrow the runtime, grammar, allowed alphabet, protocol, state transitions or signal encoding. Identify the actual restriction layer before testing tricks. Keep original Unicode/byte data and explicitly model normalization.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| eval/AST/audit hook, length or token filter | Reproduce exact Python version, filter and execution order | [Pyjails](pyjails.md), [modern methods](modern-playbook.md) |
| Restricted shell, container or VM puzzle | Read command grammar and exact sandbox boundary | [Bash](bashjails.md), [scope](../docs/SCOPE.md) |
| QR/polyglot, zero-width text or layered encoding | Magic/Unicode inventory, length/alphabet constraints | [Encodings](encodings.md), [advanced encodings](encodings-advanced.md) |
| Game, graph, SMT or optimization | Tiny exhaustive instance, invariant/recurrence, then validate optimized solver | [Games/VMs](games-and-vms.md), [recent cases](modern-playbook.md) |
| RF/SDR, DNS, invented language or strange format | Derive frame/grammar/state model before payloads; test one sample round-trip | [RF](rf-sdr.md), [DNS](dns.md), [strange formats](strange-formats.md) |

## Execute cheaply

Avoid giant expression brute force; derive grammar/evaluation/reentrancy gadgets from reachable objects. Unknown eval/pickle snippets run only in isolated local copies. Container/Kubernetes methods are only for components explicitly named as the challenge; stop at shared nodes, credentials or host mounts. Competition platform navigation is not recon; consume supplied offline exports instead.

Use the [novel problem method](../ctf-common/references/novel-problems.md) when no route matches: characterize the artifact, infer the transformation from input/output pairs, reconstruct the format/machine, and test the cheapest discriminating experiment. Do not assume every challenge is a familiar exploit class.

## Verify and finish

Verify by round-trip, re-running the game/binary with the recovered input, matching the derived sequence, or the challenge checker. A decoded string that looks like a flag is a candidate. Report the flag, the transformation/state model and solver path.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Triage](triage-reference.md), [personal learnings](personal-learnings.md), [2026 additions](upstream-2026.md). Load one to four matching sections only.
