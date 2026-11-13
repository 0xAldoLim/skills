# FAST, EXPERT and recovery

The goal is the shortest evidence-backed path, not the most elaborate plan.

## FAST

Use when the category and primitive are clear and the expected path is one to three direct checks.

1. Inventory artifacts and the flag format.
2. Run the cheapest decisive check (decode, source trace, one request, one local reproduction).
3. If it works, verify. If it fails, run one changed variant.
4. Escalate after two failures without new evidence.

Do not create subagents, a task tree or a broad scan for a one-step encoding, a known formula or a single obvious vulnerability.

## EXPERT

Use for multi-stage chains, custom implementations, heap/kernel/emulation, unusual architectures, hybrid categories, repeated strong failures or an explicit hard/no-solve label.

Maintain:

```text
solve/STATE.md       target, facts, artifacts, current primitive, next test
solve/HYPOTHESES.md  at most three active hypotheses with predicted observations
solve/evidence.jsonl optional machine-readable ledger via `../../scripts/ctf_state.py`
```

Each hypothesis records: statement, supporting evidence, cheapest discriminating test, predicted result, cost, and pivot condition. Run one test, record the observation, then update. Retire a hypothesis when its prediction fails for a controlled reason or when a cheaper stronger path exists.

## Failure classification

Before abandoning a branch, classify the failure:

| Layer | Question | Next action |
|---|---|---|
| Reachability | Did the input reach the code/parser/sink? | Fix the route, encoding or parameter |
| Parser/transform | Was it decoded, normalized or truncated? | Compare raw and processed bytes |
| Guard/filter | Did a check reject it? | Identify the exact check; do not spray variants |
| State | Did a reset, overwrite or race erase it? | Reproduce the state transition locally |
| Sink | Did the dangerous operation execute? | Instrument the sink or use a canary |
| Oracle | Is the observation reliable? | Fix the detector before changing the payload |
| Hypothesis | Was the model of the target wrong? | Replace the hypothesis |

A failed probe with an unreachable sink does not falsify the vulnerability class. Mark it blocked, record the blocker and define the unlock condition.

## Progress evaluation

After each meaningful observation, ask:

- What new fact did this produce?
- Does it change the ranking of the active hypotheses?
- Is the next step cheaper or stronger than the alternatives?
- Am I repeating a call with no changed variable?

After two no-progress branches, review the strongest unusual artifacts and blocked hypotheses. Try one unlock probe before exploring an unrelated family.

## Budgets and stop conditions

Set a budget before expensive work: requests, payload variants, brute-force space, emulation steps, search depth, wall time or tokens. Stop when the budget is exhausted or the branch is blocked. Do not turn "one more variant" into an unbounded loop.

## Recovery and continuation

Preserve state across compaction, tool failure and instance refresh:

- proven facts and rejected assumptions with reasons;
- keys, constants and offsets with their derivation;
- response fingerprints and session assumptions;
- exact next test and its predicted result.

On refresh, update scope/health, replay the smallest working request, rebuild session-specific values, and continue the existing solver. Do not restart the investigation or repeat all reconnaissance.

## Token discipline

- Read one to four matching reference sections. Use `../../scripts/lookup_knowledge.py` for line ranges.
- Hash a file once; do not re-read it unless its hash changes.
- Summarize output into a fact plus an artifact path.
- Prefer a tested helper over regenerating a long script.
- Keep summaries short and structured; do not paste full tool output into the next prompt.
- Stop a broad search when two attempts produce no new discriminating evidence.

## Escalation triggers

Escalate from FAST to EXPERT when any of these is true:

- the primitive is still unknown after cheap triage;
- two changed tests fail without new evidence;
- the path requires a chain of two or more independent primitives;
- the artifact is a custom VM/format, kernel target, heap allocator, firmware, emulator or unusual architecture;
- the challenge is marked hard/insane/zero-solve;
- a remote instance repeatedly fails health checks (stop remote work, keep local work).

Do not escalate merely because the task is unfamiliar; use [novel problems](novel-problems.md) first.
