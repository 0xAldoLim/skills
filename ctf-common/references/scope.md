# Scope: assigned challenge only

The operator-assigned challenge instance and supplied local artifacts are in scope. Competition infrastructure is not.

## In scope

- Local files supplied with the challenge.
- The exact URL, host/port, container, VM or API assigned to this challenge.
- Justified enumeration, fuzzing, bounded brute force and exploitation of that instance, within the event rules.
- Read-only public research for concepts and documentation.

## Out of scope

CTFd, scoreboards, submission APIs, competition login, provisioning, organizer VPNs, shared Docker/Kubernetes/cloud control planes, shared storage, logging, monitoring, proxies, other teams, neighboring hosts/IPs and accidentally reached internal systems. Never scan, fuzz, brute force, exploit, stress, spray credentials, escalate or move laterally against them.

Reachability, an SSRF, a recovered credential or a URL in a binary does not add authorization. A host with a supplied port authorizes that endpoint, not its other ports. A host alone authorizes small service discovery only when the challenge explicitly assigns a dedicated VM.

## Boundaries

An application RCE, jail/VM escape, Docker socket, mounted host root, node credential or cloud metadata may reveal the next layer. Determine whether it belongs to the intended challenge. If it appears shared, stop, preserve evidence and ask the operator about that exact boundary. If the flag is already obtained, finish.

Request smuggling, cache poisoning, races and controlled crashes require an isolated challenge backend. Do not poison a shared edge or crash a shared process. Confirm the boundary from source/deployment files first.

## Record

Create `solve/scope.json` from [the template](../assets/scope.json) before remote work. Record the exact target, provenance from the description, intended boundary, exclusions and a per-experiment budget. The health helper needs `kind` and `target`.

Full policy, including escape and redirect rules: [docs/SCOPE.md](../../docs/SCOPE.md).
