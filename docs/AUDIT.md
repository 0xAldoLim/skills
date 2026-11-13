# Repository audit and implementation inventory

Baseline: commit `8636995` (2026-11-12), 96 tests passed, 4 skipped (pwntools absent), validator clean.

## What was already sufficient

- Nine category skills with evidence-first triage tables and broad reference catalogs.
- Generated `INDEX.md` symptom routing and `lookup_knowledge.py` section retrieval.
- 142 protected reference prefixes with migration/correction audit.
- Crypto, pwn, archive, fuzz, health, learning, schema and installer tests.
- Tool manifest with core, category and explicit heavy tiers; missing-only/dry-run/verify.
- Personal learnings and accepted knowledge preserved outside the generated catalog.
- Scope, instance-health, workflow, learning and tooling documentation.

These were retained. Protected references were not rewritten.

## Gaps found

| Area | Gap | Action |
|---|---|---|
| Entrypoints | Nine copies of the same scope/health/execute/finish boilerplate | Added `ctf-common`; category skills now load one shared contract and keep only classification-specific triage |
| Portability | Metadata said Codex CLI/Kali; installer wrote only `~/.agents/skills` | Portable Agent Skills metadata; `--harness=agents|claude|opencode|all`; spec/portability validator |
| Trust | No dedicated prompt-injection/task-contamination protocol; fake flags and fake verification only mentioned in passing | Adversarial reference, advisory scanner, provenance/verification ladder |
| Routing | No explicit FAST/EXPERT decision or "don't over-escalate" test | `plan_solve.py`, router modes, deterministic tests |
| State | STATE/HYPOTHESES described in prose; no executable ledger separating candidate from verification | `ctf_state.py`, templates, tests |
| Coverage gaps | Custom cryptosystems, invented/strange formats, wireless/Bluetooth, OSINT cross-source verification, agent/RAG security, cloud/API boundaries, hardware/FPGA | Seven focused references, indexed |
| Retrieval | No coverage for `ctf-common`; index generator always linked `modern-playbook.md` | Generator fix; common routes and catalog |
| Tooling | No cross-platform readiness diagnostic | `install_tools.py --doctor` |
| Token budget | No measurement or enforcement | `token_audit.py`, baseline and report |
| Evaluation | No deterministic tests for traps, fake flags, routing, state, cross-harness install | `tests/test_overhaul.py` and expanded installer/provenance tests |
| Upstream | ljagiello HEAD had not been re-checked against `e79be292` | Fetched `a16e19a`; diff is evals dependency files only; documented |

## Files added

| Path | Purpose | Verification |
|---|---|---|
| `ctf-common/SKILL.md` | Shared scope/trust/routing/evidence/verification contract | validator, token audit, tests |
| `ctf-common/references/*.md` | Trap protocol, verification, workflow, novel problems, research, scope, health, tooling | links, tests |
| `ctf-common/assets/*` | STATE/HYPOTHESES/scope templates | `ctf_state.py` tests |
| `ctf-crypto/custom-systems.md` | Systematic custom-crypto analysis | index test |
| `ctf-misc/strange-formats.md` | Unfamiliar formats/invented languages | index test |
| `ctf-forensics/wireless-bluetooth.md` | Wireless/Bluetooth/RF triage | index test |
| `ctf-osint/verification-and-ethics.md` | Cross-source verification and privacy | index test |
| `ctf-ai-ml/agent-security.md` | Prompt injection/RAG/tool boundaries | index test |
| `ctf-web/cloud-and-api.md` | Cloud/container/API scope and patterns | index test |
| `ctf-reverse/hardware-and-fpga.md` | FPGA/HDL/firmware artifacts | index test |
| `scripts/ctf_state.py` | Evidence/hypothesis/candidate/verification ledger | subprocess tests |
| `scripts/scan_untrusted.py` | Advisory trap scanner | trap/benign tests |
| `scripts/plan_solve.py` | FAST/standard/EXPERT routing | mode tests |
| `scripts/token_audit.py` | Prompt-cost measurement and budget | budget test |
| `scripts/install_tools.py --doctor` | Cross-platform readiness | doctor smoke |
| `docs/RESEARCH.md`, `docs/EVALUATION.md`, `docs/TOKEN_BUDGET.md`, `knowledge/research-frameworks.json` | Research, evaluation, measurement and source ledger | ledger/docs tests |

## Files rewritten

- `README.md` for standalone installation, harness support, invocation and troubleshooting.
- `solve-challenge/SKILL.md` as a compact router.
- Nine `ctf-*/SKILL.md` entrypoints.
- `install.sh` for multiple harness roots, safe preflight/backup and no partial install.
- `scripts/validate_skills.py` for the Agent Skills spec, portability and the new contract.
- `scripts/rebuild_indexes.py` / `lookup_knowledge.py` for `ctf-common` and new references.
- `prompts/*.md` shortened and aligned with the common contract.

## Files retained

All protected reference prefixes, personal learnings, accepted knowledge records, scripts, schemas and upstream notices remain. New imports or copied code were avoided; no protected file was rewritten.
