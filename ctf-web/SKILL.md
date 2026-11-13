---
name: ctf-web
description: "Solve CTF HTTP applications, APIs, browser and authentication bugs. Use for SQLi, XSS, SSTI, SSRF, XXE, deserialization, prototype pollution, JWT/OAuth, request smuggling, cache/race bugs, GraphQL, cloud boundaries or multi-stage web chains. Pivot to crypto/reverse when that is the blocker."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred. Remote work requires the operator-assigned instance. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-web

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Map source routes, serializers, auth checks, bot behavior and dependencies before choosing a payload. Read the first baseline response and preserve session/cookie assumptions. Health and scope come before endpoint discovery.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| Generic 404, proxy failure, NXDOMAIN or timeout | Compare supplied URL and a known source route; at most three health checks | [Instance health](../docs/INSTANCE_HEALTH.md) |
| Query interpolation, ORM operators, boolean/time differences | One local boolean pair or source trace; distinguish data binding from syntax | [SQL](sql-injection.md), [server quirks](server-side-advanced-4.md) |
| Template, upload, XML, SSRF, traversal or pickle | Identify sink, parser/version and reachability; prove one read or evaluation | [Server](server-side.md), [deserialization](server-side-deser.md) |
| Admin bot, CSP, DOM or postMessage | Reproduce browser context/origin and user gesture locally | [Browser](client-side-advanced.md), [modern cases](modern-playbook.md) |
| JWT, OAuth, GraphQL, WebSocket, race, proxy/cache | Trace the exact validator and framing/state transition; use an isolated backend | [Auth](auth-jwt.md), [recent methods](modern-playbook.md) |
| Cloud/container/CI or internal service boundary | Identify the intended deployment layer before probing; metadata/internal is not automatic scope | [Cloud/API](cloud-and-api.md), [auth infra](auth-infra.md) |

## Execute cheaply

Start fuzzing only after deriving a small candidate set and a budget. Use the scoped helper in `scripts/async_fuzz.py`; redirects do not expand scope. SQLmap, ffuf and feroxbuster are optional hypothesis tools, not default recon. SSRF to cloud metadata or internal services requires evidence that the exact resource is part of the challenge. Request smuggling/cache tests require a dedicated challenge backend, not a shared competition edge.

Prefer source-guided sink analysis over blind payload storms. Stop a payload family after three variants without a changed hypothesis. Promote a finding to the main line only when it reaches the flag, source, database, privileged state or a stronger primitive.

## Verify and finish

Reconstruct the full request chain from a clean session. Verify the flag with the challenge checker, a privileged response that contains it, or a reproducible derivation. A 200 response, reflected string or admin page is not flag proof. Report the flag, verification method and solver script. Keep session tokens and flags out of reusable learning.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Modern cases](modern-playbook.md), [LEARNED](LEARNED.md), [MCP tooling](tools-mcp.md). Load one to four matching sections only.
