---
name: ctf-pwn
description: "Exploit CTF native memory corruption and low-level primitives. Use for confirmed stack, heap, format-string, ROP/SROP, seccomp, sandbox, kernel, VM or race exploitation. Use reverse engineering first when the program behavior is still unknown."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred. Executing unknown binaries requires an isolated VM/container. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-pwn

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Inspect ELF architecture, interpreter, imports, relocations, `checksec`, supplied libc/loader and source. A remote service alone does not establish a pwn primitive. Develop locally with the matching runtime and measure offsets; never reuse addresses from an unrelated example.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| Stack overwrite or format specifier control | Local cyclic offset / short leak with the correct architecture | [Overflow](overflow-basics.md), [format string](format-string.md) |
| NX, PIE, seccomp, constrained input | Read the syscall policy; measure stack alignment and allowed gadgets | [ROP](rop-and-shellcode.md), [advanced ROP](rop-advanced.md) |
| UAF, allocator metadata, largebin or FILE state | Pin libc; allocate/free a minimal local sequence; distinguish key/safe-linking | [Heap](heap-techniques.md), [FSOP](heap-fsop.md), [version notes](modern-playbook.md) |
| Kernel, CET, qemu or unfamiliar ABI | Confirm image/device/module and mitigation state; identify the primitive first | [Kernel](kernel.md), [CET](kernel-bypass.md), [modern cases](modern-playbook.md) |
| Custom VM, bytecode, sandbox or interpreter | Map opcode/state effects; find the boundary between checked and executed data | [Sandbox](sandbox-escape.md), [advanced cases](advanced-exploits.md) |
| Race, io_uring, threads or shared state | Reproduce the interleaving locally with a bounded harness | [Race notes](triage-reference.md), [modern cases](modern-playbook.md) |

## Execute cheaply

Use gdb/pwndbg and pwntools when available; fall back to `readelf`/`objdump`, struct packing and a small protocol client. `../scripts/pwn_payloads.py` generates payload bytes without connecting or executing a binary. `ctf-pwn/scripts/` contains reviewed templates; derive every offset and address.

Budget brute force, heap grooming and race attempts. Modern glibc removed hooks; pointer mangling, safe-linking, CET/shadow stacks and allocator versions require runtime validation. Prefer a leak/primitive that is stable across the supplied runtime over a fragile one-gadget chain.

Kernel/VM/container escapes stop at a shared host/node boundary. Confirm the next layer is part of the assigned challenge before interacting with it.

## Verify and finish

Demonstrate the primitive and the final read of the flag. Reproduce the exploit from a clean local state when possible, and record the exact runtime/libc. Verify the flag with the challenge checker or a controlled service response. Report offsets, primitive, verification and solver path. Capture only reusable technique, never the flag.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Attack playbook](attack-playbook.md), [static signals](static-signals.md), [payload templates](scripts/README.md). Load one to four matching sections only.
