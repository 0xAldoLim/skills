# Personal CTF solving skills for Codex CLI

Autonomous Kali-oriented solving instructions for web, pwn, crypto, reverse, forensics, OSINT, malware, misc and AI/ML. Invoke a category directly from a folder containing the challenge files and description, or use `$solve-challenge` when the category is unclear. Short entrypoints route to symptom indexes and detailed references; verified personal knowledge remains traceable in the migration audit.

## Install and use

```bash
git clone https://github.com/0xAldoLim/skills.git
cd skills
sh install.sh --dry-run
sh install.sh
```

The default links complete category directories into ~/.agents/skills, so references and shared helpers resolve to this checkout. Keep the checkout available. For a standalone installation, use `sh install.sh --copy`: it includes category directories plus docs, scripts, schemas, knowledge and prompts. Existing destinations are preserved unless --replace is supplied; replacements receive a sibling backup outside skill discovery. SKILLS_DIR overrides the destination. Installing skills does not install tools.

```bash
python3 scripts/install_tools.py core web --dry-run
python3 scripts/install_tools.py core web --missing-only
source ~/.local/share/ctf-tools/venv/bin/activate
cd /path/to/challenge-folder
codex
# Use $ctf-web and find the flag.
# Use $solve-challenge and find the flag.
```

`all` selects ordinary category tooling. `heavy` is an explicit separate tier for Sage, Ghidra, QEMU, GNU Radio, symbolic execution and large ML frameworks. --verify checks readiness without installing; --dry-run prints the plan without modifying the system. Native package availability and heavy workflows require validation on the actual Kali release.

## Solving contract

Analyze local files first, preserve originals and persist STATE.md/HYPOTHESES.md in solve/. Test the cheapest strong hypothesis before expensive tools or remote work; deepen analysis automatically for hard/custom/zero-solve challenges. All direct category entrypoints enforce the supplied challenge-instance boundary. Shared platforms, scoreboard/submission APIs, provisioning, networks, nodes and other teams remain outside scope. Repeated proxy/expiry failures trigger a bounded health check and instance refresh while local analysis continues. Live research targets concepts and technical documentation, never the exact active challenge solution.

Verify a recovered flag before declaring success. Automatically capture only understood, materially useful, reproducible, reusable novel methods or verified prerequisite variants; do not save secrets or flags in reusable knowledge. A polished writeup, platform submission and GitHub push require a separate request.

## References and maintenance

- [Operations](docs/OPERATIONS.md): paths, setup, update, validation and state
- [Workflow](docs/WORKFLOW.md), [scope](docs/SCOPE.md), [instance health](docs/INSTANCE_HEALTH.md), [learning](docs/LEARNING.md), [tools](docs/TOOLS.md)
- [Research ledger](knowledge/research-sources.json): dated sources, prerequisites, confidence and reproduction status
- [Preservation audit](knowledge/migration/section-map.json): original root sections and destinations
- [Implementation report](docs/OVERHAUL_REPORT.md) and [machine-readable report](knowledge/overhaul-report.json)

The inactive original-baseline.zip retains the original tracked files, including superseded platform instructions. Do not extract that archive into an installed skills discovery directory. MIT-licensed upstream imports retain their source pin; independently written research notes link to their original authors and do not copy third-party exploit code.
