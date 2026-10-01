---
name: ctf-pwn
description: "Exploit CTF native memory corruption and low-level primitives to recover a flag. Use for confirmed stack, heap, format-string, kernel or sandbox exploitation; use reverse first when the program behavior is still unknown."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-pwn

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Inspect ELF architecture, interpreter, imported symbols, relocations, checksec, supplied libc/loader and source. A remote service alone does not establish a pwn primitive. Develop locally with matching runtime and record offsets from measurements.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| Stack overwrite or format specifier control | Local cyclic offset / short leak with the correct architecture | [Overflow](overflow-basics.md), [format string](format-string.md) |
| NX, PIE, seccomp, constrained input | Read syscall policy; measure stack alignment and allowed gadgets | [ROP](rop-and-shellcode.md), [advanced ROP](rop-advanced.md) |
| UAF, allocator metadata, largebin or FILE state | Pin libc, allocate/free a minimal local sequence; distinguish key from safe-linking | [Heap](heap-techniques.md), [FSOP](heap-fsop.md), [version notes](modern-playbook.md) |
| Kernel, CET, qemu or unfamiliar ABI | Confirm supplied image/device/module and mitigation state; identify primitive first | [Kernel](kernel.md), [CET](kernel-bypass.md), [modern cases](modern-playbook.md) |

Use gdb/pwndbg and pwntools when available; fallback to readelf/objdump, struct packing and a small protocol client. Helper `../scripts/pwn_payloads.py` generates payload bytes without connecting or executing a binary. Never reuse gadget addresses or libc offsets from an unrelated example. Hooks removed in modern libc, pointer mangling, safe-linking and shadow stacks require runtime-specific validation. Kernel/VM escapes stop before a shared host/node.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
- [Complementary upstream techniques](upstream-2026.md) — load matching sections only.
