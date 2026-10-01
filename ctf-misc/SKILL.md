---
name: ctf-misc
description: "Solve CTF jails, unusual encodings, language/runtime puzzles, games, RF and constraints that do not fit a clearer category. Use as a cross-category fallback; pivot to the specialized skill when its primitive becomes dominant."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-misc

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Use evidence to narrow the runtime, grammar, allowed alphabet, protocol, state transitions or signal encoding. Identify the actual restriction layer before testing tricks. Keep original Unicode/byte data and explicitly model normalization.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| eval/AST/audit hook, length or token filter | Reproduce exact Python version, filter and execution order | [Pyjails](pyjails.md), [modern methods](modern-playbook.md) |
| Restricted shell, container or VM puzzle | Read command grammar and exact sandbox boundary | [Bash](bashjails.md), [scope](../docs/SCOPE.md) |
| QR/polyglot, zero-width text or layered encoding | Magic/Unicode inventory, length/alphabet constraints | [Encodings](encodings.md), [polyglots](encodings-advanced.md) |
| Game, graph, SMT or optimization | Tiny exhaustive instance, invariant/recurrence, then validate optimized solver | [Games/VMs](games-and-vms.md), [recent cases](modern-playbook.md) |
| RF/SDR, DNS or blockchain | Derive frame/contract/state model before payloads | [RF](rf-sdr.md), [DNS](dns.md), [Web3](../ctf-web/web3.md) |

Avoid giant expression brute force; derive grammar/evaluation/reentrancy gadgets from reachable objects. Unknown eval/pickle snippets run only in isolated local copies. Container/Kubernetes methods are only for components explicitly named as the challenge; stop at shared nodes, credentials or host mounts. Competition platform navigation is not recon; consume supplied offline exports instead.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
- [Complementary upstream techniques](upstream-2026.md) — load matching sections only.
