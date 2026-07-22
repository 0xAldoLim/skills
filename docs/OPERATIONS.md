# CTF Skill Operations on Kali Linux

## Architecture

The repository remains a normal filesystem Agent Skills collection:

```text
solve-challenge/SKILL.md        unknown or mixed challenge dispatcher
ctf-*/SKILL.md                 direct category entry points
ctf-*/INDEX.md                 generated symptom-to-reference maps
ctf-*/*.md                     detailed authored techniques
ctf-*/LEARNED.md               append-only accepted additions
prompts/*.md                   category prompt templates
knowledge/                     integrity, provenance, inbox, and ledger
scripts/                       deterministic routing and learning utilities
tests/                         validation and policy tests
```

The intended workflow stays simple:

```text
Get challenge -> create a challenge directory -> add files and description
-> select or classify a $ctf-* skill -> run Codex in that directory
-> recover and verify the flag -> capture reusable learning if warranted
```

## Install on Kali

```bash
git clone git@github.com:0xAldoLim/skills.git
cd skills
./install.sh
```

The installer copies complete skill directories into `~/.agents/skills`, including supporting references, indexes, learned entries, and `agents/openai.yaml`. It does not delete local-only files at the destination.

Equivalent manual installation:

```bash
mkdir -p ~/.agents/skills
cp -a ctf-* solve-challenge ctf-writeup ~/.agents/skills/
```

## Update

```bash
cd ~/skills
git pull --ff-only
./install.sh
```

If the checkout lives elsewhere, use that path. To install into a different Agent Skills directory:

```bash
SKILLS_DIR=/path/to/skills ./install.sh
```

## Direct invocation and dispatcher use

When the category is clear, invoke it directly:

```text
Use $ctf-reverse to solve the challenge in the current directory.
Read the challenge description and inspect the provided files first.
Recover and verify the flag.
```

Use `$solve-challenge` for unknown or mixed bundles. Category `name` and `description` frontmatter drive discovery; `agents/openai.yaml` adds a visible default `$skill-name` prompt without rewriting original frontmatter.

## Challenge workspace

```text
challenge-name/
├── DESCRIPTION.md
├── input/                  supplied files, unchanged
├── output/                 carved or generated artifacts
└── solve/                  scripts, transcripts, and notes
```

Run prompt generation from the repository:

```bash
python3 scripts/generate_prompt.py \
  --description "$(< /path/to/challenge/DESCRIPTION.md)" \
  --workspace /path/to/challenge
```

Pass `--category ctf-reverse` when known and `--remote target.example:31337` only when a remote target is part of the challenge. Templates exist for every major category; users never need internal reference filenames.

## Evidence-first solving

The dispatcher establishes facts before classification, selects one primary and at most two secondary categories, and keeps at most three hypotheses. Each hypothesis records supporting and contradicting evidence, the cheapest discriminator, expected result, and pivot condition. Category indexes map artifact, symptom, primitive, framework, architecture, and cross-category signals to a small set of references.

## Automatic learning

Create a record conforming to `schemas/learning.schema.json`, then capture it:

```bash
python3 scripts/capture_learning.py solve/new-learning.json --auto
```

Automatic acceptance requires a verified flag, material contribution, reuse beyond one challenge, reproducibility, high category confidence, and no equivalent technique. Accepted records append to `ctf-<category>/LEARNED.md` and the JSONL ledger. The pipeline never replaces an existing entry. Failed guesses, unverified payloads, accidents, and speculation are rejected; uncertain or related candidates go to `knowledge/inbox/`.

## Inbox review

```bash
python3 scripts/classify_learning.py knowledge/inbox/<candidate>.json
python3 scripts/detect_duplicates.py knowledge/inbox/<candidate>.json
python3 scripts/append_learning.py knowledge/inbox/<candidate>.json --approved
python3 scripts/rebuild_indexes.py
```

Approve a variant only when architecture, operating system, runtime, framework, encoding restriction, mitigation, primitive, or remote/local behavior is meaningfully different. Identify the original technique in the record. Move rejected candidates into `knowledge/rejected/` while retaining the ledger event.

## External enrichment

`knowledge/sources.yaml` and `sources.lock.json` pin repository URLs, exact commits, and licenses. `knowledge/enrichment-report.json` records overlap, duplicate score, decision, reason, and destination. To run a broad conservative heading comparison against already-cloned sources:

```bash
python3 scripts/enrich_from_sources.py \
  --source ljagiello-ctf-skills /tmp/ljagiello-ctf-skills \
  --source yaklang-hack-skills /tmp/yaklang-hack-skills
```

Generated candidates default to inbox unless an exact duplicate is skipped. Human review must distill concepts in original wording, use safe placeholders, and retain source path, commit, and license. Never import full files or payload catalogs.

## Append-only guarantees

`knowledge/integrity-manifest.json` stores each protected path, original size, SHA-256, and protected byte length. Validation hashes exactly that original prefix and permits only appended bytes:

```bash
python3 scripts/verify_append_only.py
```

Generated indexes may be rebuilt. Authored knowledge may not be deleted, shortened, reordered, or rewritten.

## Human-review escalation

Human review is allowed only for a concrete visual, auditory, physical-context, or interpretive limitation after relevant machine methods are exhausted. Record the artifact, attempted methods, conflicting candidates, recognized reason, narrow question, and empty remaining-machine-options list. Validate it with:

```bash
python3 scripts/human_review_gate.py output/unsolved-status.json
```

Tool absence, script errors, initial failure, misclassification, or untried analysis never satisfy the gate.

## Validation

```bash
python -m pytest tests/ -v
python scripts/verify_append_only.py
python scripts/validate_skills.py
python scripts/rebuild_indexes.py --check
python scripts/check_repository_safety.py
```

When installed, also run `pre-commit run --all-files`.

## Recovery and rollback

Before rollback, preserve any new inbox records or challenge-local solve scripts. Inspect history and create a recovery branch rather than force-pushing:

```bash
git log --oneline --decorate -10
git switch -c recovery/preserve-learning
git revert <commit-to-revert>
```

To restore the installed copy from a known repository revision, check out that revision in a separate worktree or clone and run its installer. Never truncate a protected file to undo an appended entry; use a follow-up correction entry and ledger event.
