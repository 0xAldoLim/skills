# Challenge instance scope

Use the organizer-supplied challenge instance and supplied local artifacts to recover the flag. A challenge URL, host/port, dedicated VM, per-team container, API, or explicitly assigned SSH target is in scope. Record the exact resource, provenance from the description, and intended application/container/VM boundary in `solve/scope.json` before remote work.

Normal solving does not need repeated permission: inspect files, extract into a work directory, write and debug scripts, test local payloads, make targeted HTTP/protocol requests, enumerate justified endpoints, fuzz, and use bounded searches against that instance. Reduce the search space using source, constraints, mathematics, or an offline oracle first. Record the budget and stop condition before remote brute force, races, or fuzzing. Respect stricter competition rules.

## Infrastructure is a different scope

CTFd, scoreboard, competition login, submission API, provisioning system, organizer VPN, shared Docker hosts, Kubernetes nodes/orchestrators, cloud control plane, shared storage/databases, logging, monitoring, unrelated proxies, other teams, neighboring hosts/IPs, and accidentally reached internal systems are out of scope. Never probe, scan, enumerate, fuzz, brute force, exploit, stress, DoS, spray credentials, escalate privileges, or move laterally against them. Reachability, a recovered credential, or an SSRF does not grant scope. An exact component is an exception only when the challenge explicitly names it as its target.

A host with a supplied port authorizes that endpoint; it does not authorize scanning its other ports. When a host alone is assigned as a dedicated challenge VM, small service discovery may be justified. Do not broaden into subdomains, adjacent addresses, CIDRs, platform hosts, or other challenges. Public-source OSINT and documentation research are passive reads; they do not authorize testing those sources.

## Stop at the boundary

An application RCE, jail escape, VM escape, Docker socket, mounted host root, node credential, cloud metadata, or cluster service may reveal the next layer. Before interacting with that layer, determine whether it belongs to the intended challenge. If it appears shared, stop, preserve the evidence, and document the boundary without using secrets. If the flag is obtained, finish. If the challenge requires an escape but the next layer's ownership is unclear, ask the user to resolve that exact boundary. Do not continue automatically.

HTTP redirects, DNS changes, URLs recovered from binaries, C2 domains, callbacks, and internal addresses in captures are evidence, not additional targets. Do not follow a cross-origin redirect until the description establishes that endpoint as part of the challenge. Recovered malware infrastructure is analyzed offline or emulated locally.

Request smuggling, cache poisoning, races, and controlled crashes require an isolated challenge backend/connection. Do not poison a shared edge or crash a shared process. Confirm the boundary locally from source/deployment files first.

## Minimal scope record

```json
{
  "kind": "challenge_instance",
  "target": "https://target.example:8443/",
  "assignment": "Exact URL supplied in challenge description",
  "boundary": "Per-team application container",
  "excluded": ["scoreboard", "shared host", "other teams"],
  "remote_budget": {"requests": 100, "concurrency": 2, "stop_on": "boundary or instance failure"}
}
```

Budgets are per experiment, not universal defaults. The health helper only needs the first two fields; its check is an endpoint guard, not a network sandbox for arbitrary exploit scripts.
