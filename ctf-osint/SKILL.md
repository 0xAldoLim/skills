---
name: ctf-osint
description: "Solve CTF public-source identity, location and historical evidence puzzles. Use for geolocation, public profiles, archives, DNS/CT, metadata and transport/public records; do not actively test discovered infrastructure."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-osint

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Extract image metadata, text, crop clues, timestamps, usernames and identifiers before searching. Maintain an evidence chain with query, source, capture/publication dates, inference and confidence. Exact answer verification is usually multi-source consistency, not a flag-looking string.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| Landmark, road, logo or historical photo | Metadata/OCR and reverse image; combine visual constraints and local language | [Geolocation](geolocation-and-media.md), [modern cases](modern-playbook.md) |
| Username, reused avatar, platform ID | Public profile and archive comparison, not login/password testing | [Social](social-media.md) |
| DNS/WHOIS/CT, Git history or archived pages | Passive record/export/history lookup, confirm relevant date | [Web/DNS](web-and-dns.md) |
| Aircraft, vessel, transport or public records | Correlate identifier, route and time zone with documented provenance | [Detailed triage](triage-reference.md) |

Use English, Indonesian and Malay query variants when geography warrants them; preserve original spellings. Treat OCR and reverse-image results as candidates. Street numbering, renamed venues, timezone conversions and archival timestamps can differ: verify the requested time period and object. Do not mass-enumerate users or test discovered hosts. If perception remains necessary, provide the crop, candidate locations, concrete distinguishing feature, and exact observation requested.

- [Detailed existing techniques](triage-reference.md) — load matching sections only.
