# Implementation report

Status: complete for the deterministic scope. Commit: see `git log -1` (the report is committed with the change).

## What changed

- Added a shared `ctf-common` skill and references for scope, untrusted content, evidence/verification, FAST/EXPERT workflow, novel problems, research, instance health and tooling.
- Rewrote the nine category entrypoints and the `solve-challenge` router to load the shared contract and keep only category-specific triage/execution.
- Added seven focused references for gaps: custom cryptosystems, strange/invented formats, wireless/Bluetooth, OSINT cross-source verification, agent/RAG security, cloud/API boundaries and hardware/FPGA.
- Added executable helpers: `ctf_state.py` (evidence/hypothesis/candidate/verification ledger), `scan_untrusted.py` (advisory trap scanner), `plan_solve.py` (FAST/standard/EXPERT), `token_audit.py` (prompt-cost budget), and `install_tools.py --doctor`.
- Made the installer harness-aware: `~/.agents/skills`, `~/.claude/skills`, `~/.config/opencode/skills`, or all three; safe preflight, backups, copy/link modes.
- Updated the Agent Skills metadata, indexes, prompts, README and maintainer documentation.
- Added deterministic tests for metadata, links, routing, traps, fake flags, state bounds, cross-harness installation and the research/source ledger.

The full inventory and rationale are in [AUDIT.md](AUDIT.md). The machine-readable summary is [overhaul-report-2026-11-12.json](../knowledge/overhaul-report-2026-11-12.json).

## Research

Reviewed and pinned:

- OpenCode-for-CTF `6b432a43`
- D-CIPHER / nyuctf_agents `612190f2`
- EnIGMA arXiv:2409.16165
- CTFAgent / CTFKnow (CCS 2025)
- PentestGPT `e8b1bb77`
- CTFusion `16798200`
- AgentLSD arXiv:2609.19140
- CTF-ABACUS arXiv:2608.26237
- Gray Swan indirect prompt injection arXiv:2603.15714
- HackSynth `48a41f79`
- Arditi et al. arXiv:2406.11717 (background only; no refusal bypass)
- ljagiello/ctf-skills HEAD `a16e19a` vs integrated `e79be292`
- PRESTIGE as a research reference only

The ljagiello HEAD diff contains only `evals` dependency files; no skill content changed. Details and adoption decisions: [RESEARCH.md](RESEARCH.md), [research-frameworks.json](../knowledge/research-frameworks.json).

## Prompt-injection and provenance defenses

- Challenge content is labeled data, never an instruction source.
- Trap families from AgentLSD are handled explicitly: goal hijack, false authority, false validation, exploration bait, time sink.
- Concealment is accounted for: inspect tool calls/side effects, not only the final answer (Gray Swan).
- Candidate provenance is ranked: checker/derivation/commitment > runtime/derived > static > model.
- `ctf_state.py` refuses `claim`, `format`, `regex`, `scan`, `readme`, `model` and `tool` as verification methods, and refuses to verify a `claim`-origin candidate.
- `scan_untrusted.py` is advisory and does not block legitimate analysis of malicious code, credentials or flags.
- Tests cover a forged README/system message, a fake "verified" claim, a decoy flag and a benign security sentence.

## Token efficiency

Entrypoint bodies dropped 18.5-42.0% (category skills 32.3-42.0%, router 18.5%). Repeated category loads are ~620-800 estimated tokens instead of ~1100-1260. The first category load now includes the one-time ~1266-token shared contract, so it is not lower than a bare old category file; it replaces duplicated/linked safety material and adds trust/verification/state guidance. Full measurements and interpretation: [TOKEN_BUDGET.md](TOKEN_BUDGET.md).

## Tooling

- `install.sh` supports three harness roots, `--copy`, `--replace`, `--dry-run`, `SKILLS_DIR` and safe backups.
- `install_tools.py` retains core/category/heavy tiers, missing-only, dry-run, verify, Sage fallback and adds read-only `--doctor`.
- Heavy stacks were not installed. No Docker, PRESTIGE, MCP or model gateway is required to load or use the skills.

## Validation

Local Kali Linux, Python 3.13.12:

```text
pytest:                 108 passed, 4 skipped (pwntools absent)
validate_skills.py:     passed
rebuild_indexes --check: current
check_repository_safety: passed
verify_append_only:     142 protected references intact
audit_snippets:         0 syntax errors; 1082 contextual Python fences; 11 Sage fences
token_audit --check:    passed
ruff -F:                passed
```

The 4 skips are optional pwntools payload-generation checks; the pure-Python payload ABI checks still pass. CI is configured for Ubuntu Python 3.11/3.12; remote CI status must be checked after push.

## Real-model evaluation

Not run. No private challenge corpus, no authorized paid inference and no live competition were used. No solve-rate, token or elapsed-time improvement is claimed. The protocol for a future A/B/C comparison is in [EVALUATION.md](EVALUATION.md).

## Remaining limitations

- Scanner heuristics miss paraphrases, images and encoded instructions; findings are not proof and clean scans are not immunity.
- The state helper records that a verification method was used; it cannot establish that the underlying checker is trustworthy.
- Routing is heuristic for hybrid challenges.
- Heavy Sage/Ghidra/QEMU/GPU stacks and every Windows/WSL package combination were not exercised.
- Historical references remain large and are only partially reproduced; targeted retrieval reduces context but does not guarantee every legacy snippet runs.
- The upstream pwnable.tw writeup tree was reviewed but not imported; its primitives are covered locally.
