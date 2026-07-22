# Personal Codex Skills

This repository stores root `SKILL.md` files for personal CTF skills.

## Install

```sh
git clone git@github.com:0xAldoLim/skills.git
cd skills
./install.sh
```

The installer creates `~/.agents/skills` if needed. If a skill directory
already exists, only its root `SKILL.md` is replaced.

To install somewhere else:

```sh
SKILLS_DIR=/path/to/skills ./install.sh
```

## Append-only Optimization Layer

Routing, prompt generation, integrity guarantees, indexes, learning review, enrichment provenance, and Kali operations are documented in [docs/OPERATIONS.md](docs/OPERATIONS.md). Existing knowledge remains protected by `knowledge/integrity-manifest.json` and `scripts/verify_append_only.py`.
