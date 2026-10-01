# CTF skill operations on Kali

## Architecture and paths

Each ctf-*/SKILL.md is a direct operational entrypoint. INDEX.md provides symptom routes and a compact catalog; detailed *.md and learned/*.md references load only when evidence calls for them. The dispatcher uses artifact magic and a native vulnerability discriminator rather than treating every remote service as pwn. ctf-writeup is used only on request. Existing agents/openai.yaml metadata supports category discovery.

Helpers resolve relative to the loaded skill, not the challenge working directory. REPO_ROOT is the complete checkout/installed bundle; SKILL_DIR is the selected category. The challenge keeps originals in place or input/, generated files in output/ and state/scripts in solve/.

## Installation, replacement and updates

Run `sh install.sh --dry-run`, then `sh install.sh`. The default uses complete-directory symlinks into ~/.agents/skills; preserve the checkout. --copy also installs docs/scripts/schemas/knowledge/prompts at the bundle root so relative references work. Existing targets cause a preflight failure before any installation. --replace moves conflicts into a sibling .ctf-backup-<pid> directory before copying/linking. Review backups before removing them. Source and destination must differ even when the destination uses .. or symlink aliases.

On a copied installation, preserve local learned references and accepted records before replacing the bundle; merge them back using the learning review and rebuild indexes. A symlinked checkout keeps new learning in the repository. Updating from Git must preserve local edits/records. There is no automatic push, destructive reset or host-wide install in the solving workflow.

## Tools and fallbacks

```bash
python3 "$REPO_ROOT/scripts/install_tools.py" core crypto --dry-run
python3 "$REPO_ROOT/scripts/install_tools.py" core crypto --missing-only
python3 "$REPO_ROOT/scripts/install_tools.py" core crypto --verify
source ~/.local/share/ctf-tools/venv/bin/activate
```

Actual installs use apt-get for missing system packages and pip inside a dedicated venv for missing importable modules; no sudo pip. --dry-run and --verify do not create a venv or install packages. `all` excludes heavy; add `heavy` explicitly when needed. Failed apt names/imports/shared libraries are reported. Run apt-get update separately only when repository metadata needs it. Use [TOOLS.md](TOOLS.md) for lightweight alternatives before large downloads or computations.

## Solve state and exact scope

Initialize solve/STATE.md with assignment, file hashes, proven facts, offsets/keys/constants, response fingerprints and next tests. HYPOTHESES.md records each hypothesis, evidence, cheapest discriminator, predicted observation, outcome and pivot condition. Optional findings.json stores machine-readable facts. Never erase failed hypotheses after a refresh. Record the new endpoint and replay the smallest already-working request before continuing.

Create solve/scope.json using the example in [SCOPE.md](SCOPE.md); each target is explicitly assigned, with no wildcard, range, subnet or credential-bearing URL. Run instance_health.py with that file before remote exploitation. At most three short requests/connections, verified TLS and no redirects prevent the health gate from becoming enumeration. DNS/slow response work is bounded by a subprocess deadline. A single 404/500 or silent TCP server is inconclusive; repeated expiry/proxy/transport failure is likely unavailable and requires refresh. Keep useful local development running.

## Retrieval and automatic learning

```bash
python3 "$REPO_ROOT/scripts/lookup_knowledge.py" 'Coppersmith unbalanced unknown divisor' --category ctf-crypto --limit 4
python3 "$REPO_ROOT/scripts/capture_learning.py" solve/learning.json --auto --dry-run
python3 "$REPO_ROOT/scripts/capture_learning.py" solve/learning.json --auto
```

Inspect neighboring concepts and explicit runtime/architecture/mitigation/parser/oracle/constraint/framework/version/protocol dimensions before declaring novelty. Strong unique/verified variants need no manual approval. A fuzzy/title overlap enters the inbox, while verification/materiality/understanding gates remain mandatory even with --approved. Promotion writes a targeted reference, catalog pointer, generated index and ledger; a failed promotion restores existing files. Concurrent promotion is refused with a lock; after a crash, inspect the recorded PID and state before removing a stale lock. Do not concurrently hand-edit the same category during promotion.

## Validation and preservation

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pytest PyYAML jsonschema ruff
python3 -m pytest tests/ -q
python3 scripts/verify_append_only.py
python3 scripts/validate_skills.py
python3 scripts/rebuild_indexes.py --check
python3 scripts/check_repository_safety.py
ruff check scripts tests --select F
```

The historical verifier filename remains compatible, but its v2 manifest checks migration completeness and normalized protected reference prefixes. It verifies the inactive original snapshot, original section hashes, documented correction/supersession reasons and verbatim relocated personal sections. Never regenerate a baseline to hide missing knowledge. Planned explanatory corrections require a reasoned migration update. INDEX.md is generated and can change; verified learned additions remain separate and original LEARNED pointers append.

Python snippets are syntax-audited separately from execution. Sage notation and deliberate sketches are labeled; successful parsing does not establish runtime correctness. Tests use synthetic arithmetic/archive/HTTP/payload fixtures, not live competition attacks. Windows/Git Bash validation here does not prove Kali package availability, heavy runtime compatibility or successful reproduction of every researched challenge. See the implementation report for exact counts and limits.
