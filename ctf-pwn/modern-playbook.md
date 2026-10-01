# ctf-pwn modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Safe Rust compiler lifetime bug becomes UAF

**Signal / prerequisite:** A lifetime coercion permits a Box reference after destruction.
**Cheapest useful test:** Reproduce allocation/drop order and dangling reads locally with supplied compiler/libc.
**Primitive and method:** Establish the concrete UAF first, then allocator reuse and leak/write reachability. The published glibc 2.31 hook path requires that older runtime.
**Failure / wasted work:** Safe-linking and removal of malloc hooks change later exploit stages; do not reuse the old final target on modern glibc.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/sigpwny/UIUCTF-2024-Public/blob/073cb80f1f42669252e88020fdb5b281f031c693/challenges/pwn/rusty-pointers/SOLVE.md).

## One payload interpreted by two child binaries

**Signal / prerequisite:** Shared-memory input reaches different binaries with a narrow syscall filter and closed descriptors.
**Cheapest useful test:** Map each read offset and one common-address gadget in both children.
**Primitive and method:** Build a payload satisfying both layouts and divergent gadget effects. Use the descriptor returned by open, and account for both children exiting normally.
**Failure / wasted work:** Assuming fd=3 or ignoring the second child can invalidate an otherwise correct ORW chain.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; two local traces, layout assertions and measured static gadget tables.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/pwn/mysterious_vault/solve/WRITEUP.md).

## Patched eBPF rotate range unsoundness

**Signal / prerequisite:** The supplied verifier treats rotate as monotone over a min/max interval.
**Cheapest useful test:** Enumerate a small interval and compare true rotated extrema with verifier bounds.
**Primitive and method:** Use a local counterexample to establish verifier/runtime disagreement before analyzing the challenge kernel primitive.
**Failure / wasted work:** This is a challenge-patched verifier, not a stock-kernel claim; the writeup includes weakened mitigations and speculative stages.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; small integer counterexample generator; dedicated VM only.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/pwn/rolling_around/solve/WRITEUP.md).

## Image predictor leaks uninitialized heap then indexes wide pixels

**Signal / prerequisite:** A modified JPEG XL decoder skips initialization for some image shapes and treats wide values as palette indices.
**Cheapest useful test:** Trace allocation size/reuse and one east-predictor value locally.
**Primitive and method:** Recover the seeded heap data as pixels; separately prove the palette OOB read/write and exact index arithmetic. Check RELRO before any GOT target.
**Failure / wasted work:** Allocation shape and patched opcodes are essential; these are not ordinary JPEG XL guarantees.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/nautilus-institute/quals-2025/blob/94ef8d5614c0b7dd49135e2bbc15e0a947e6ee2d/jxl4fun/solver/readme.md).

## snprintf would-have-written length skips a canary

**Signal / prerequisite:** A cursor advances by snprintf return values; a parser permits a boundary-length hostname.
**Cheapest useful test:** Use a truncated local string and compare returned count with actual bytes written.
**Primitive and method:** Derive the resulting cursor displacement and overwrite range. Prove that the actual writes skip rather than overwrite the canary; satisfy saved-register and final gadget constraints.
**Failure / wasted work:** A one_gadget address without its register/memory constraints is insufficient.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/hackthebox/cyber-apocalypse-2025/blob/843bdcc55112c5b68b05b5fe706fbbb1dad9b551/pwn/%5BHard%5D%20Vault/README.md).

## Narrowed line length enables a heap callback overwrite

- **Signal:** getline length narrows to signed short before a bound check and a later strcpy.
- **Cheap test:** Measure the conversion at 32768 bytes using a benign local line.
- **Method:** Trace the accepted negative length to callback storage; prove executable-page configuration, leak-based PIE addressing and actual argument registers before building the payload.
- **Failure / pivot:** ABI register residue and executable allocation are exact-build prerequisites. Embedded nulls truncate strcpy; a crash alone proves neither controllable callback nor code execution.
- **Verification:** Use local debugger evidence for overwrite, callback target and arguments. Source reviewed; challenge not locally reproduced.
- **Source:** [Gabriel; Hack.lu CTF 2024](https://gabri3l.net/2024-hacklu-ctf-gymnotes/)
