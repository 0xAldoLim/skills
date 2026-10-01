# Verified learning and promotion

After a verified successful solve, automatically capture a method when it materially contributed, is understood, reproducible, reusable or strategically valuable, and the repository does not already explain it adequately. No manual approval is required for strong unique candidates or verified prerequisite variants. Never push automatically.

Write a record conforming to [the learning schema](../schemas/learning.schema.json). Include signals, exact preconditions, cheapest test, real primitive, implementation/commands, verification evidence, failure modes, when not to use, related references, confidence and date. Do not include flag values, passwords, temporary hosts, instance IDs, credentials, failed guesses, unexplained accidents or speculative successes. Use artifact hashes and local proof summaries rather than secrets.

```bash
python3 "$REPO_ROOT/scripts/capture_learning.py" solve/learning.json --auto
```

The pipeline validates the record, checks authored section bodies and accepted records, and compares concept/primitive/preconditions. Identifiers/titles/code are hints, not sufficient semantic evidence when runtime, architecture, mitigation, parser, oracle, constraint, framework, version or protocol changes the method. Put those explicit differences in `variant_dimensions`. A shared title with a changed known prerequisite can be a useful variant. Fuzzy text similarity is a conservative review heuristic, not a claim of embedding-based semantic understanding. Inspect the retrieved neighboring technique before deciding novelty.

Strong records become targeted `ctf-*/learned/<technique>.md` references, a small `LEARNED.md` pointer and an updated category index. Existing personal LEARNED entries and accepted external-enrichment records remain intact; external research does not falsely claim a live verified flag. Uncertain/related records enter `knowledge/inbox/` for later generalization. Rejected or unverified inbox guesses do not prevent a later verified learning. The ledger records each decision and destination.

For promotion of an inbox record, inspect the related reference and prerequisites, fix missing evidence or generalize the useful variant, then rerun capture; use a new filename/title if the previous inbox path exists. `append_learning.py --approved` may resolve a semantic-review ambiguity but cannot bypass flag/material contribution/reusability/reproducibility gates. Do not promote misunderstood behavior just because a flag appeared once.

Refresh generated indexes with `scripts/rebuild_indexes.py` after manual edits. Search only likely category references with `scripts/lookup_knowledge.py --category ctf-crypto 'small errors reused modulus' --limit 4`. Novelty and references are reviewed again during repository maintenance; immutable records preserve provenance while explanatory Markdown may be reorganized with a migration reason.
