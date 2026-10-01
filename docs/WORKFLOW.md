# Autonomous solving workflow

Resolve helper/reference paths relative to the loaded skill file, never relative to the challenge working directory. `REPO_ROOT` means the repository checkout or installed bundle root; `SKILL_DIR` means its category directory. Do not assume `scripts/` in the challenge folder belongs to the skills bundle.

1. Read the description, flag format, supplied files and exact instance assignment. Inventory hidden files, magic bytes, sizes and hashes; search obvious flag candidates. Preserve originals in place or `input/`, extract copies into `output/`, and put scripts/state in `solve/`. Do not execute an unknown artifact just to identify it.
2. For remote work, establish [scope](SCOPE.md) and run the [health gate](INSTANCE_HEALTH.md). Continue useful local analysis if the instance is unavailable. Source and binaries usually permit local payload development first.
3. Select a primary category from evidence and a secondary skill only when the current blocker crosses categories. Open its `INDEX.md`, then one to four likely references. A filename, banner, status code, or unverified crash is a clue rather than proof.
4. In normal mode maintain up to three strong active hypotheses. Each records evidence, cheapest discriminator, predicted observation, cost, and pivot condition. Run the cheapest test; update facts when the result contradicts the hypothesis. Prefer byte/constraint models, offline samples, small differential tests, and minimal reproducible scripts over broad tool runs.
5. Escalate depth automatically for zero solves, high difficulty, custom implementation, heavy obfuscation, hybrid problems, or repeated strong failures. Exhaustive mode expands local analysis, mathematics, emulation, technical research, and experimental coverage. It never expands target scope. Fast mode uses obvious signatures and direct tests; normal mode balances investigation and cost.
6. Maintain `solve/STATE.md`, `solve/HYPOTHESES.md`, and optionally `solve/findings.json`: proven facts, rejected assumptions and reasons, keys/constants/offsets, environmental constraints, response fingerprints, next tests, and flag evidence. State survives compaction and instance refresh. Budget expensive searches and estimate feasible work before starting them.
7. Verify a recovered flag by the challenge's actual checker, reproducible derivation, authenticated successful response, or supplied artifact semantics. A regex match alone is a candidate; inspect decoys, provenance and output. Do not submit to a platform API unless the user separately requested submission.
8. Return the flag, why it is valid, a short technical path, and useful solver artifacts. Generate a polished writeup only when `$ctf-writeup` is requested. Then [capture novel verified knowledge](LEARNING.md) automatically; never auto-push.

## Research during a live solve

Search techniques, official documentation, algorithms, papers, runtime/source behavior, CVEs, analogous vulnerabilities and tool usage. Do not search the exact active challenge name combined with writeup/solution/flag, nor retrieve an exact solution from an archive. Historical exact writeups may be researched during repository enrichment; this exception does not carry into live competition solving.

## Human perception and genuine blockers

Use machine extraction and available local alternatives first. When the remaining step genuinely needs visual/audio interpretation, give the artifact, region/time span, candidate interpretations, reason it discriminates, and exact observation needed. Do not demand literal exhaustion of all conceivable machine work; request the smallest useful human input while independent analysis continues. Missing tools, one script failure, or a category pivot alone are not perception blockers.

Do not stop because a hard challenge is inconvenient while a meaningful, feasible technical path remains. An unsolved report must preserve facts, failed hypotheses, remaining surface/tests, missing information, compute/tool limits and instance status. A scope boundary or unavailable service blocks dependent work; state the exact dependency instead of presenting it as a solved challenge.
