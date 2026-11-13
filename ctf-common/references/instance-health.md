# Cheap instance health gate

Before deep remote analysis, check the exact assigned endpoint. Do not inspect provisioning or the platform to debug a broken instance.

## HTTP

One short DNS/TCP/TLS/HTTP attempt plus at most two known-route or HEAD discriminators. Record status, interesting headers, a bounded body fingerprint, expected application markers and time. Do not follow redirects; verify TLS.

```bash
python3 "$REPO_ROOT/scripts/instance_health.py" \
  --scope solve/scope.json --known-route /login \
  --expected 'Challenge title' --output solve/health.json
```

## Raw TCP

Connect once with a timeout and read a bounded banner. A silent service can be healthy: classify it as inconclusive until a known protocol response discriminates. Use `--probe-hex` only for a small explicitly chosen message.

## Interpretation

| Evidence | Decision |
|---|---|
| Expected challenge content/route, including an intentional 404/500 with markers | Reachable; continue |
| One ordinary 404/500 without markers | Inconclusive; compare source/description and one known route |
| Repeated default-backend 404, container/deployment not found, explicit expiry, 410 without expected app | Likely expired; stop remote exploitation |
| Repeated 502/503/504 with generic proxy body | Likely unavailable after the small budget |
| Repeated NXDOMAIN, refused or timeouts on the exact endpoint | Likely unavailable; ask for refresh |
| TLS validation error | Inconclusive transport/config; do not silently disable TLS |
| Login/redirect/generic 2xx placeholder | Reachable but unconfirmed |

A proxy response alone is not proof of expiry: some challenges intentionally target routing. Supply an application marker.

## Stop and resume

Report: `Likely expired or unavailable`, the minimal evidence, and `Refresh/restart the instance and provide the new URL/host`. Continue useful local analysis. Preserve state, tested payloads, offsets, session assumptions and the next experiment. On refresh: update scope, rerun health, replay the smallest working request, rebuild session values, continue the existing solver.

Full policy: [docs/INSTANCE_HEALTH.md](../../docs/INSTANCE_HEALTH.md).
