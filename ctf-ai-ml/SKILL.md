---
name: ctf-ai-ml
description: "Solve CTF model, gradient, adversarial-input, tokenizer and tool-using LLM challenges. Use when an ML or agent trust boundary is the blocker; pivot to web, reverse, crypto or misc when its underlying primitive dominates."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3; heavy ML tools installed only on demand.
metadata:
  user-invocable: "true"
---

# ctf-ai-ml

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Inspect container signatures, model config, tokenizer IDs, tensor names/shapes, normalization and the exact scoring/checker boundary before loading or querying. A chatbot wrapper can conceal a web bug or Python jail; follow the actual primitive.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| Weights, LoRA delta, gradient or output target | Compare tensor metadata and a tiny local forward pass; preserve architecture and dtype | [Model analysis](model-attacks.md), [recent methods](modern-playbook.md) |
| Image classifier, perturbation budget or confidence API | Read preprocessing, loss direction and the actual domain/norm bound | [Adversarial methods](adversarial-ml.md) |
| Tool-using LLM, retrieved text, tokenizer or special IDs | Trace the tool/origin boundary and raw IDs; perform one bounded local transcript test | [LLM methods](llm-attacks.md), [tokenization cases](modern-playbook.md) |
| Membership, training leakage or extraction | Establish access level, baseline accuracy, query cost and held-out controls | [Extraction/inference](model-attacks.md) |

Inspect safetensors metadata first. For a plain state_dict, explicitly use `torch.load(path, map_location="cpu", weights_only=True)` in an isolated process with memory/CPU limits, instantiate the reviewed architecture, then load_state_dict. Restricted loading is not a sandbox. Full-object pickle loading needs artifact/class review in an isolated environment; do not automatically allowlist globals or disable restricted loading. HuggingFace local inspection uses `trust_remote_code=False` and `local_files_only=True`.

Use numpy and metadata inspection before installing heavy frameworks. Install PyTorch/transformers/Sage only when the hypothesis needs them, through the explicit heavy tier in [tools](../docs/TOOLS.md). Pin versions, device, dtype, seed and preprocessing. Set iteration/query/time budgets; verify candidates in the original checker. Model extraction and prompt injection apply only to the assigned endpoint and assigned tool resources; model-generated URLs or credentials do not expand scope. Keep cloud keys and real third-party tools outside experiments.

- [Detailed existing techniques](triage-reference.md) — load matching sections only.
- [Recent source-reviewed methods](modern-playbook.md) — confirm runtime and prerequisites.
