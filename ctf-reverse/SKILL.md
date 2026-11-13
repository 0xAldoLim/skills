---
name: ctf-reverse
description: "Understand and solve compiled, packed or obfuscated CTF targets: ELF, PE, Mach-O, Go, Rust, .NET, Java, Android, WebAssembly, Python bytecode, firmware, FPGA/HDL artifacts and custom VMs. Use before exploitation when behavior, transform or validation logic is the blocker."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred. Executing unknown samples requires isolation. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-reverse

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Identify format, architecture, runtime, packed/tail data and the validation boundary. Start with symbols, imports, strings, constants and a small call graph. Work backwards from success/check sites rather than decompiling everything.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| ELF/PE, Go/Rust/C++/Swift runtime | readelf/objdump or PE metadata; locate comparison and input path | [Languages](languages-compiled.md), [recent cases](modern-playbook.md) |
| JNI/Android, WASM, .NET, Python/Java bytecode | Extract the container; inspect entrypoints and native callbacks | [Platforms](platforms.md), [languages](languages-platforms.md) |
| VM dispatch or flattened state machine | Trace a short input; build opcode/state table and validate one step | [Patterns](patterns.md), [VM examples](patterns-ctf.md) |
| Decompiler fails, anti-debug, packed code or MMIO | Verify architecture/code boundaries; emulate only the decisive routine | [Emulation](unicorn-emulation.md), [anti-analysis](anti-analysis.md) |
| HDL/bitstream, FPGA, logic analyzer or firmware image | Identify the device/toolchain and recover the logic or data path before emulating | [Hardware/FPGA](hardware-and-fpga.md) |
| Mixed boolean arithmetic or optimizer-resistant code | Simplify with an equivalence check, then validate against the original | [MBA](mba-simplification.md), [r2pipe](radare2-r2pipe.md) |

## Execute cheaply

Prefer Ghidra headless when useful, then rizin/radare2, then objdump/readelf plus Capstone/Unicorn. Use angr/Z3 only for a tractable slice with modeled I/O and concrete checks; validate the candidate in the original checker. Extractor/runtime tools must match version/ABI. Execute unknown samples only in an isolated local environment; inspect static code first.

Route to [pwn](../ctf-pwn/SKILL.md) after identifying a real corruption primitive, or [crypto](../ctf-crypto/SKILL.md) after lifting exact equations. Do not reverse every function when one comparison or one transform is decisive.

## Verify and finish

Validate the recovered input/flag in the original binary or a faithful reimplementation. For a transform, show the inverse round-trips a supplied sample. For a key, show the decryption reproduces known plaintext. Report the flag, the decisive routine and solver path. Capture only reusable technique.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Tools](tools.md), [dynamic tools](tools-dynamic.md), [emulation](tools-emulation.md), [MCP](tools-mcp.md). Load one to four matching sections only.
