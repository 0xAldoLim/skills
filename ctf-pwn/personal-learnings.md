# Personal verified challenge learnings

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-19

- **Kernel ioctl disclosure before corruption:** When a misc device ioctl takes a small userspace struct like `{ size, ptr }`, do not assume the attacker-controlled size means an overflow. Reconstruct the full dispatcher first, identify the real ioctl command, and check whether helpers read from a fixed privileged path and return a filtered slice or selected line instead of raw file contents.
- **Clamp semantics matter:** If the returned length is clamped to a post-processed line or helper-selected slice, classify the primitive as disclosure rather than memory corruption. That changes the workflow from exploit-building to controlled extraction and proof of reachability.

