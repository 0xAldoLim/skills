# Prompt-loading cost

Measurements use `ceil(characters / 4)` as a deterministic approximation. This is **not** a provider billing tokenizer and must not be reported as billed usage. Run:

```bash
python3 scripts/token_audit.py --check
python3 scripts/token_audit.py --baseline knowledge/validation/token-baseline.json
```

Baseline: `knowledge/validation/token-baseline.json` from commit `8636995`. New: 2026-11-12.

## Entrypoint bodies

Frontmatter is excluded, matching the body an agent loads after activation.

| Skill | Before chars | After chars | Change |
|---|---:|---:|---:|
| ctf-ai-ml | 5054 | 2961 | -41.4% |
| ctf-crypto | 4677 | 3156 | -32.5% |
| ctf-forensics | 4391 | 2586 | -41.1% |
| ctf-malware | 4270 | 2478 | -42.0% |
| ctf-misc | 4492 | 2654 | -40.9% |
| ctf-osint | 4274 | 2580 | -39.6% |
| ctf-pwn | 4530 | 3068 | -32.3% |
| ctf-reverse | 4372 | 2791 | -36.2% |
| ctf-web | 4563 | 2986 | -34.6% |
| solve-challenge | 4641 | 3784 | -18.5% |
| ctf-writeup | 1456 | 1456 | unchanged |
| find-skills | 5086 | 5086 | unchanged |

The nine category entrypoints no longer repeat scope, health, finish and learning boilerplate. Their remaining ~620-800 estimated tokens are category-specific triage and execution.

## Shared contract cost

`ctf-common/SKILL.md` adds ~1266 estimated tokens once per session when a category skill is invoked directly. Category + common is ~1886-2055 estimated tokens on first load:

| Category | Category + common |
|---|---:|
| ctf-malware | 1886 |
| ctf-forensics | 1913 |
| ctf-osint | 1911 |
| ctf-misc | 1930 |
| ctf-reverse | 1964 |
| ctf-ai-ml | 2007 |
| ctf-web | 2013 |
| ctf-pwn | 2033 |
| ctf-crypto | 2055 |

Honest interpretation:

- **Repeated category loads are cheaper:** 620-800 tokens per later category instead of 1100-1260.
- **First category load is not lower** than a bare old category file: it now includes the one-time trust/verification contract that was previously duplicated or left in linked docs. The old files also linked scope/health/workflow/learning docs; when those were actually read, total context was comparable or larger.
- **Listing metadata** is compact: 3,421 characters for all skill descriptions.

## Budgets enforced in CI

| Budget | Limit |
|---|---:|
| Category body | 1000 estimated tokens |
| `ctf-common` body | 1400 estimated tokens |
| Category + common | 2300 estimated tokens |
| Description | 1024 characters |
| Compatibility | 500 characters |
| All listing descriptions | 12,000 characters |

These are guardrails against re-bloating entrypoints, not claims about model billing. Detailed technique references remain lazy and are not counted until loaded.
