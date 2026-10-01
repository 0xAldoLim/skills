# ctf-ai-ml modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Indirect nickname injection reaches a tool

**Signal / prerequisite:** Attacker-controlled nickname text returns through an account-detail tool.
**Cheapest useful test:** Set an inert nickname marker and inspect the actual tool/result transcript.
**Primitive and method:** Locate the data/instruction confusion at the tool boundary; test a single goal-directed instruction and verify the restricted tool invocation, not just a confident model reply.
**Failure / wasted work:** Model behavior is stochastic; budget attempts and context resets. Tool text is untrusted data, not authority.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; small transcript-driven candidate queue.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/ai/ductfbank-2/solve/WRITEUP.md).

## Agent tool injection chains into backend SQL

**Signal / prerequisite:** An injected tool result steers a second account-detail call with unsafe backend input.
**Cheapest useful test:** Inspect tool arguments and reproduce the SQL parameter boundary locally.
**Primitive and method:** Separate prompt control from SQL control; match SQLite query shape/UNION arity, and verify the resulting backend response and flag independently.
**Failure / wasted work:** The chain fails if tool policy or parameter binding blocks either step; prose claims alone are not a primitive.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/ai/ductfbank-3/solve/WRITEUP.md).

## Weights encode integer characters

**Signal / prerequisite:** A small state_dict has unusually integer-valued tensor patterns.
**Cheapest useful test:** Inspect shapes, ranges and diagonals using restricted state_dict loading.
**Primitive and method:** Test reversible integer-to-byte interpretations on targeted tensors; preserve dtype/endian/scaling and verify output structure before optimization.
**Failure / wasted work:** Loading a full pickled model can run code; weight steganography needs no training or GPU.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; tensor summary, diagonal/residual byte scans.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/hackthebox/cyber-apocalypse-2025/blob/843bdcc55112c5b68b05b5fe706fbbb1dad9b551/machine_learning/ml_enchanted_weights/README.md).

## Dataset context changes a protected prediction

**Signal / prerequisite:** A protected row cannot change but model scoring depends on the submitted dataset.
**Cheapest useful test:** Confirm all validation constraints and the target-row checksum locally.
**Primitive and method:** Manipulate eligible context rows while satisfying every constraint; use a small experiment matrix to distinguish refitting, normalization and ranking effects.
**Failure / wasted work:** Do not call this universal training poisoning; the exact scoring/data path is required. Preserve CSV types and row identity.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; constraint-preserving CSV transforms and measured score logs.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/hackthebox/cyber-apocalypse-2025/blob/843bdcc55112c5b68b05b5fe706fbbb1dad9b551/machine_learning/ml_wasteland/README.md).

## Embedding inversion requires the matching encoder

**Signal / prerequisite:** An embedding array names a recognizable encoder family.
**Cheapest useful test:** Inspect shape/norm and confirm encoder/tokenizer/corrector compatibility.
**Primitive and method:** Try the matching inversion corrector with explicit step/beam/resource budgets; compare the reconstructed text by re-embedding before one challenge-instance test.
**Failure / wasted work:** A generic decoder cannot invert arbitrary embeddings; GPU/model downloads are heavy and approximate text may need exact normalization.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; offline inversion with pinned model revisions and similarity checks.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/hackthebox/cyber-apocalypse-2025/blob/843bdcc55112c5b68b05b5fe706fbbb1dad9b551/machine_learning/ml_reverse_prompt/README.md).
