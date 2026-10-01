---
name: ctf-web
description: "Solve CTF HTTP applications, APIs, browser and authentication bugs. Use when a web trust boundary is the path to the flag; pivot to crypto or reverse when that becomes the blocker."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-web

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Map source routes, serializers, auth checks, bot behavior and dependencies before choosing a payload. Read the first baseline response and preserve session/cookie assumptions. Health comes before endpoint discovery.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| Generic 404, proxy failure, NXDOMAIN, timeout | Compare supplied URL and known source route; at most three health checks | [Instance health](../docs/INSTANCE_HEALTH.md) |
| Query interpolation, ORM operators, boolean/time differences | One local boolean pair or source trace; distinguish data binding from syntax | [SQL](sql-injection.md), [server quirks](server-side-advanced-4.md) |
| Template, upload, XML, SSRF, traversal or pickle | Identify sink, parser/version and needed reachability; prove one read or evaluation | [Server](server-side.md), [deserialization](server-side-deser.md) |
| Admin bot, CSP, DOM or postMessage | Reproduce browser context/origin and user gesture locally | [Browser](client-side-advanced.md), [modern cases](modern-playbook.md) |
| JWT, OAuth, GraphQL, WebSocket, race, proxy/cache | Trace exact validator and framing/state transition; use isolated backend | [Auth](auth-jwt.md), [recent methods](modern-playbook.md) |

Start fuzzing only after deriving a small candidate set and budget. Use the scoped helper in `scripts/async_fuzz.py`; redirects do not expand scope. SQLmap, ffuf and feroxbuster are optional hypothesis tools, not default recon. SSRF to cloud metadata or internal services requires evidence that the exact resource is part of the challenge. Request smuggling/cache tests require a dedicated challenge backend, not a shared competition edge.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
