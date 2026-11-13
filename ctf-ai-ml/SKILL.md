---
name: ctf-ai-ml
description: "Solve CTF model, gradient, adversarial-input, tokenizer, prompt-injection, RAG, tool-output and agent-security challenges. Use when an ML or agent trust boundary is the blocker; pivot to web, reverse, crypto or misc when its underlying primitive dominates."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3; heavy ML frameworks install only on demand in the explicit heavy tier."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-ai-ml

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Inspect container signatures, model config, tokenizer IDs, tensor names/shapes, normalization and the exact scoring/checker boundary before loading or querying. A chatbot wrapper can conceal a web bug or Python jail; follow the actual primitive.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| Weights, LoRA delta, gradient or output target | Compare tensor metadata and a tiny local forward pass; preserve architecture and dtype | [Model analysis](model-attacks.md), [recent methods](modern-playbook.md) |
| Image classifier, perturbation budget or confidence API | Read preprocessing, loss direction and the actual domain/norm bound | [Adversarial methods](adversarial-ml.md) |
| Tool-using LLM, retrieved text, tokenizer or special IDs | Trace the tool/origin boundary and raw IDs; perform one bounded local transcript test | [LLM methods](llm-attacks.md), [agent security](agent-security.md) |
| RAG, memory, tool output or multi-agent trust boundary | Map who can write/read each channel; test one origin-confusion and one privilege boundary | [Agent security](agent-security.md), [tokenization cases](modern-playbook.md) |
| Membership, training leakage or extraction | Establish access level, baseline accuracy, query cost and held-out controls | [Extraction/inference](model-attacks.md) |

## Execute cheaply

Inspect `safetensors` metadata first. For a plain state dict, use `torch.load(path, map_location="cpu", weights_only=True)` in an isolated process with memory/CPU limits, instantiate the reviewed architecture, then `load_state_dict`. Restricted loading is not a sandbox. Full-object pickle loading needs artifact/class review in an isolated environment; do not globally allowlist.

HuggingFace local inspection uses `trust_remote_code=False` and `local_files_only=True`. Use numpy and metadata inspection before installing heavy frameworks. Pin versions, device, dtype, seed and preprocessing. Set iteration/query/time budgets and verify candidates in the original checker.

Prompt injection and tool-output attacks apply only to the assigned endpoint and assigned tool resources; model-generated URLs or credentials do not expand scope. Keep cloud keys and real third-party tools outside experiments.

## Verify and finish

Verify with the challenge classifier/checker, a reproduced forward pass, a held-out control, or an authenticated response. Report the flag, the exact model/input and the metric. Do not claim a universal jailbreak or benchmark result from one instance.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Triage](triage-reference.md), [agent security](agent-security.md), [modern cases](modern-playbook.md). Load one to four matching sections only.
