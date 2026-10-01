# Cheap instance health gate

Before deep remote analysis, inspect the exact supplied hostname/port/path. Preserve local artifacts and `solve/STATE.md` while checking the service. Do not inspect provisioning APIs or the platform to debug a broken instance.

For HTTP, use a short DNS/TCP/TLS/HTTP attempt and at most two additional known-route or HEAD discriminators. Save status, headers of interest, a bounded body fingerprint, expected application markers, and the time. The helper performs at most three GETs, verifies TLS, caps body reads, and does not follow redirects:

```bash
python3 "$REPO_ROOT/scripts/instance_health.py" \
  --scope solve/scope.json --known-route /login --expected 'Challenge title' \
  --output solve/health.json
```

For raw TCP, connect once with a timeout and read a bounded banner. Use an expected protocol message only when the protocol requires input. The helper supports `--probe-hex` for an explicitly chosen small message. A silent service can be healthy; classify it as inconclusive until a known protocol response discriminates.

## Evidence, not status-code folklore

| Evidence | Decision and next action |
|---|---|
| Expected challenge content/route is present, including an intentional 404 or 500 | Application reachable; continue the relevant hypothesis |
| One ordinary 404/500 without application markers | Inconclusive; compare description/source and one known route |
| Repeated default-backend 404, container/deployment not found, explicit expiry, or 410 with no expected application | Likely expired/unprovisioned; stop remote exploitation |
| Repeated 502/503/504 with generic proxy/unavailable body | Likely unavailable; stop after the small confirmation budget |
| Repeated NXDOMAIN, refused connections, or timeouts on the exact supplied endpoint | Likely unavailable; request refresh, also distinguish local network failure |
| TLS validation error | Inconclusive transport/configuration failure; check supplied scheme/hostname, do not silently disable TLS |
| Login/redirect/generic 2xx placeholder | Reachable but application unconfirmed; establish what the challenge should serve |

Check hostname against the supplied instance, expected routes in source, challenge wording, headers/body, DNS and TLS where informative. A response mentioning a proxy alone is not sufficient: some challenges intentionally target routing. Supply an application marker to avoid classifying deliberate proxy behavior as dead.

## Stop and resume

Report: `Likely expired or unavailable`, exact minimal evidence, and `Refresh/restart the instance and provide the new URL/host`. Continue useful offline analysis; stop dependent remote attempts. Record last verified facts, tested payloads, state/session assumptions, and next experiment. When a refreshed endpoint arrives, update scope and health, rerun the inexpensive baseline, rebuild session-specific values, and replay the existing solver. Do not discard or redo local analysis.

An outage is an external-state blocker, not a reason to expand scope, reconstruct imaginary routes, or repeatedly spend context. This gate applies to web, pwn, crypto oracles, misc services, AI endpoints, and malware C2 simulations.
