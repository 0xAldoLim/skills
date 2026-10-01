---
name: ctf-reverse
description: "Understand and solve compiled, packed or obfuscated CTF targets: native binaries, bytecode, APK/JNI, WASM, firmware and custom VMs. Use before exploitation when behavior, transform or validation logic is the blocker."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-reverse

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Identify format, architecture, runtime, packed/tail data and validation boundary. Start with symbols, imports, strings, constants and a small call graph. Work backwards from success/check sites rather than decompiling everything.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| ELF/PE, Go/Rust/C++/Swift runtime | readelf/objdump or PE metadata; locate comparison and input path | [Languages](languages-compiled.md), [recent cases](modern-playbook.md) |
| JNI/Android, WASM, .NET, Python/Java bytecode | Extract container; inspect entrypoints and native callbacks | [Platforms](platforms.md), [languages](languages-platforms.md) |
| VM dispatch or flattened state machine | Trace a short input; build opcode/state table and validate one step | [Patterns](patterns.md), [VM examples](patterns-ctf.md) |
| Decompiler fails, anti-debug, packed code or MMIO | Verify architecture/code boundaries; emulate only the decisive routine | [Emulation](unicorn-emulation.md), [anti-analysis](anti-analysis.md) |

Prefer Ghidra headless when useful, then rizin/radare2, then objdump/readelf plus Capstone/Unicorn. Use angr/Z3 only for a tractable slice with modeled I/O and concrete checks; validate a candidate in the original checker. Extractor/runtime tools must match version/ABI. Execute unknown samples only in an isolated local environment; inspect static code first. Route to pwn after identifying a real corruption primitive, or crypto after lifting exact equations.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
