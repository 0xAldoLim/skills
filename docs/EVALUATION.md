# Evaluation

## Deterministic suite

Run from the repository root:

```bash
python3 -m pytest -q
python3 scripts/validate_skills.py
python3 scripts/rebuild_indexes.py --check
python3 scripts/check_repository_safety.py
python3 scripts/audit_snippets.py
python3 scripts/token_audit.py --check
python3 scripts/install_tools.py all --dry-run
ruff check scripts tests --select F
```

The suite establishes:

| Property | Test |
|---|---|
| Every `SKILL.md` parses; name/description/license/compatibility follow the Agent Skills spec | `tests/test_skills.py`, `test_overhaul.py` |
| Category entrypoints are compact and load the shared contract | `test_overhaul.py` |
| Internal links resolve | `validate_skills.py`, `test_skills.py` |
| Indexes are deterministic and include new references | `test_indexes.py`, `test_overhaul.py` |
| Scripts compile and shell scripts parse | `test_quality.py` |
| Crypto/pwn/archive/fuzz helpers work on synthetic fixtures | `test_helpers.py`, `test_pwn_payloads.py`, `test_poly1305.py` |
| Installer copies/links correctly, preflights conflicts, backs up, supports three harness roots | `test_installer.py`, `test_overhaul.py` |
| Routing selects a category and does not over-escalate simple tasks | `test_classification.py`, `test_overhaul.py` |
| Prompt-injection and fake-evidence text is flagged but does not change the task | `test_overhaul.py` |
| Fake flags and "claim" verification are not accepted | `test_overhaul.py` (`ctf_state.py`) |
| Max three active hypotheses is enforced | `test_overhaul.py` |
| Protected knowledge and append-only references remain intact | `test_integrity.py` |
| Learning schema, duplicate detection and atomic promotion still work | `test_learning*.py`, `test_schema.py` |

Deterministic tests prove mechanism, not model capability. A clean scanner result is not universal immunity.

## Optional real-model comparison

Where an operator has an authorized OpenCode/Codex/Claude Code installation, a private challenge corpus and a budget, compare three conditions:

| Arm | Condition |
|---|---|
| A | Plain harness, no CTF skills |
| B | Previous skills checkout (`8636995`) |
| C | This overhaul |

Protocol:

1. Use fresh, independently authored or permission-cleared challenges not used during development. Do not retrieve writeups or answer keys.
2. Use a fresh workspace per run and a fixed prompt template. Record harness version, model ID, provider, temperature/effort, time budget, token budget and tool permissions.
3. Blind the solver to the expected flag. Verification happens outside the solver workspace with the operator's checker or commitment.
4. Run at least three trials per challenge per arm, or report the exact smaller design.
5. Record: independent solve (checker/commitment), time, input/output tokens (or unknown), tool calls, turns, duplicate calls, and whether a fake flag/decoy was submitted.
6. Score provenance, not just the flag: intended exploit, runtime exposure, derivation, lookup, recall, guess or unsupported claim.
7. Report all challenges, including failures. Do not filter to solved cases. Do not claim statistical significance from a small sample.
8. Keep traces private if they contain challenge files, flags or provider data.

Suggested output:

```json
{
  "harness": "opencode",
  "model": "provider/model",
  "arm": "C",
  "challenge": "private-fixture-01",
  "independent_solve": true,
  "verification": "checker",
  "provenance": "derived",
  "elapsed_seconds": 0,
  "tokens": {"input": null, "output": null},
  "turns": 0,
  "tool_calls": 0,
  "duplicate_calls": 0,
  "decoy_submitted": false,
  "notes": ""
}
```

## What was actually run for this overhaul

- The full deterministic suite was run locally on Kali Linux with Python 3.13. Results are reported in [OVERHAUL_REPORT.md](OVERHAUL_REPORT.md).
- No paid inference, no private challenge corpus and no live competition were used. Therefore no solve-rate, token or elapsed-time improvement is claimed.
- The AgentLSD/CTF-ABACUS principles are implemented as mechanisms and tested with synthetic traps, not as a reproduced benchmark.

## Limitations

- The scanner is heuristic and can miss paraphrases, images and encoded instructions; it can also flag legitimate security examples.
- `ctf_state.py` verifies that a verification method and result were recorded, not that the underlying checker is trustworthy. Checker provenance remains a human/operator decision.
- Category routing is lexical/heuristic and can be wrong on hybrid challenges; the router instructs the agent to inspect evidence.
- No heavy tool tier (Sage, Ghidra, QEMU, GPU ML) was installed or exercised for this revision.
- Windows/WSL behavior is covered by portable logic and shell parsing, not full end-to-end tool installation.
