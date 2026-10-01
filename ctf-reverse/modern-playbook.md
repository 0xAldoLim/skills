# ctf-reverse modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## XFG metadata encodes a stateful maze

**Signal / prerequisite:** A cell call kills the process unless its CFG membership/type hash permits it.
**Cheapest useful test:** Map the function-pointer array and load-config table before brute force.
**Primitive and method:** Extract passable cells and switch instructions that mutate other cell hashes; search over position plus switch state, then encode moves and invert the final transform.
**Failure / wasted work:** Position-only BFS loses door state; this challenge edits mitigation metadata rather than bypassing XFG generally.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; PE metadata parser and state-aware graph search.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/project-sekai-ctf/sekaictf-2025/blob/683dd81ae520581add40ec21c4819866e28cbde4/reverse/miku-music-machine/solution/README.md).

## Python embeds a native validator

**Signal / prerequisite:** A Python artifact carries a DLL and callback-mediated flag checks.
**Cheapest useful test:** Carve the PE and inspect imports/exports plus callback arguments.
**Primitive and method:** Lift each native constraint and map shared globals back to Python. Verify candidate behavior across both layers.
**Failure / wasted work:** Reading only the high-level bytecode misses native checks; executing the wrapper on the host is unnecessary.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/rev/bilingual/solve/WRITEUP.md).

## Encrypted Godot pack plus game state

**Signal / prerequisite:** A Godot executable contains an encrypted resource pack and a state/time-dependent check.
**Cheapest useful test:** Locate pack metadata and the key handling in the supplied runtime.
**Primitive and method:** In isolated execution recover the actual key, extract the pack, inspect scripts and reconstruct the required state transitions.
**Failure / wasted work:** Not every exported game has a recoverable embedded key; patched gameplay should still validate the real secret relation.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; pack extraction and scripted state replay.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/rev/godot/solve/WRITEUP.md).

## Swift string checks in UI closures

**Signal / prerequisite:** Validation is hidden among many SwiftUI symbols and onChange closures.
**Cheapest useful test:** Demangle symbols, locate the input callback and its data accesses.
**Primitive and method:** Follow the closure into string transforms; preserve Unicode/String indexing semantics and compare local input/output cases.
**Failure / wasted work:** Decompiler byte offsets may not match Swift grapheme or scalar semantics.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/rev/swiftpasswordmanager-crackme/solve/WRITEUP.md).

## Modified emulator contains encoded checker data

**Signal / prerequisite:** A supplied qemu-riscv64 carries a custom transformed table.
**Cheapest useful test:** Compare emulator code/data with the expected build; inspect table references.
**Primitive and method:** Recover exact byte order, invert each modular affine step and enumerate only the short within-block permutations; verify with the original checker.
**Failure / wasted work:** Hardcoded file offsets and charset in the solve are instance-specific, not reusable constants.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/SECCON/SECCON13_online_CTF/blob/32d98bc7af7159877dd90d96b44f93d00f9e49b3/reversing/qrackv/solver/solve.py).

## Scored constraints permit optimization shortcuts

**Signal / prerequisite:** The checker accepts a score threshold instead of all conditions.
**Cheapest useful test:** Lift a small condition subset with exact bit width and signedness.
**Primitive and method:** Use a weighted objective or bounded genetic search with a faithful local score function; validate intermediate candidates against the original checker. An impossible conjunction does not require proving every soft constraint.
**Failure / wasted work:** Unjustified charset assumptions, signed comparison errors and chasing an unnecessary optimum waste time.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** high; local score evaluator, Z3 Optimize model callback or bounded evolutionary search.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://kako57.github.io/posts/plaid-2025-prospectin/).

## Recover Go names before lifting HTTP handlers

- **Signal:** A stripped Go executable contains runtime metadata and HTTP handlers.
- **Cheap test:** Identify the Go version and recover symbols with a compatible GoReSym/Ghidra workflow.
- **Method:** Find the handler, preserve string pointer/length pairs and decode little-endian comparisons before reconstructing query checks and byte transforms.
- **Failure / pivot:** Decompiler variables can misrepresent Go ABI and map iteration; confirm against instructions rather than copied pseudocode.
- **Verification:** Replay lifted checks offline and compare to the original dedicated checker. Source reviewed; challenge not locally reproduced.
- **Source:** [whyuhurtz; IDSECCONF 2025 Finals](https://whyuhurtz.me/2025/11/ctf-idsecconf-2025-finals-writeup/)

## Byte stores wrap wider arithmetic

- **Signal:** A PE decoder computes signed arithmetic on dword constants then stores bytes.
- **Cheap test:** Inspect destination store width and decode one constant.
- **Method:** Apply the observed arithmetic modulo 256 at the byte store, retaining wider intermediate behavior.
- **Failure / pivot:** Python negative values do not wrap automatically; confirm any configuration branch first.
- **Verification:** Compare decoded bytes and branch predicates with a local checker. Source reviewed; challenge not locally reproduced.
- **Source:** [whyuhurtz; IDSECCONF 2025 Finals](https://whyuhurtz.me/2025/11/ctf-idsecconf-2025-finals-writeup/)
