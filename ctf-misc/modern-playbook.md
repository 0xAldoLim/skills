# ctf-misc modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Split ZIP parsers follow a symlink volume

**Signal / prerequisite:** unzip extracts entries while 7z later interprets split archive volume names.
**Cheapest useful test:** Reproduce the two parser stages in a disposable directory with harmless files.
**Primitive and method:** Map extraction/link handling and split-volume naming; test a local dummy volume before any challenge-only file read.
**Failure / wasted work:** Generic guarded extraction intentionally rejects these links; traversal behavior requires exact tool versions and a dedicated target.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/misc/dualzip/solve/WRITEUP.md).

## Read-budgeted filesystem walk

**Signal / prerequisite:** A disk service exposes few bytes rather than a whole image.
**Cheapest useful test:** Read the superblock and derive block/inode/descriptor sizes.
**Primitive and method:** Follow only metadata needed for the requested path; cache reads, batch contiguous ranges and tally bytes before each request.
**Failure / wasted work:** Hardcoded filesystem offsets fail on different features or layouts; reading whole directories can consume the budget.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; bounded ext metadata walker and byte ledger.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/misc/for_golf_hard/solve/WRITEUP.md).

## Round-robin file chunk interleave

**Signal / prerequisite:** Several PNG signatures recur at regular chunk offsets.
**Cheapest useful test:** Test a small chunk-size/stream-count hypothesis on copies.
**Primitive and method:** Deinterleave whole chunks while preserving tails, then validate each output signature, structure and PNG CRCs.
**Failure / wasted work:** A readable header alone does not validate the split; truncate nothing until the final tail is accounted for.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/misc/scrapbooking/solve/WRITEUP.md).

## Pickle parser disagreement under byte limits

**Signal / prerequisite:** Python unpickler, C unpickler and pickletools disagree on tiny inputs.
**Cheapest useful test:** Compare inert scalar/stack opcodes under the exact Python version in isolation.
**Primitive and method:** Build an outcome matrix for each implementation; minimize a payload matching the requested error pattern. Disassembly success does not prove unpickling safety.
**Failure / wasted work:** Whitespace, null handling, empty append and stack invariants differ by implementation/version; never unpickle arbitrary downloaded objects on the host.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; isolated differential harness with per-case timeout.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/project-sekai-ctf/sekaictf-2025/blob/683dd81ae520581add40ec21c4819866e28cbde4/misc/discrepancy/solution/README.md).

## HDL literal width prunes impossible branches

**Signal / prerequisite:** Seven-bit inputs are compared with sized and unsized decimal constants.
**Cheapest useful test:** Write down bit widths, signedness and truncation for one branch.
**Primitive and method:** Evaluate comparisons using HDL rules; remove only provably impossible cases, or run a local simulator and parse its output.
**Failure / wasted work:** Sized constants truncate; unsized constants and context-dependent signedness differ. Blind integer translation changes semantics.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; iverilog/verilator simulation or width-aware constraints.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/uclaacm/lactf-archive/blob/3379d4a7b36680764a34e7dc817cc3c94c244764/2026/misc/not-just-a-hobby/solve.md).

## Token IDs need the exact tokenizer and special tokens

**Signal / prerequisite:** Integer sequences resemble vocabulary IDs and include unusually high markers.
**Cheapest useful test:** Check vocabulary ranges and a small reversible decode under candidate encodings.
**Primitive and method:** Decode with the evidenced tokenizer, distinguishing ordinary and special token IDs. Preserve every original ID and explicitly label unknown IDs instead of silently dropping them.
**Failure / wasted work:** Wrong encoding can produce plausible text; the source shortcut discarded special tokens and should not become a general rule.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** low; tokenizer decode/re-encode checks.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://rustybladez.medium.com/0ctf-2024-writeup-numbers-a0139658076b).
