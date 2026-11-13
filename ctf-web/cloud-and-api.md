# Cloud, container and API boundaries

Use only when the challenge explicitly includes the cloud/container/API component. A metadata service, internal endpoint or cloud credential found by accident is not authorization.

## Identify the intended boundary

- Application container vs sidecar vs shared node.
- Object storage bucket, queue, database, function, metadata endpoint or control plane.
- CI/CD runner, build cache, artifact registry or deployment secret.
- API gateway, service mesh, internal DNS or admin service.

Read Dockerfile, compose, Kubernetes manifests, CI config and deployment scripts before probing. The challenge description must establish the component as part of the target.

## Cheap tests

| Evidence | Test |
|---|---|
| App runs in a container | Inspect mounts, env names (not values), cgroup limits and exposed ports from source |
| SSRF-like fetch | Use a canary URL you control or a challenge-local listener; do not scan internal ranges |
| Object storage reference | Check the exact bucket/path named by the challenge; test read/write semantics |
| CI/deployment artifact | Inspect build logs, cached layers and artifact metadata supplied with the challenge |
| API auth boundary | Compare roles, object IDs, tenant IDs and method-level checks |
| GraphQL | Introspection if enabled; query/mutation authz; batching/aliasing; depth/cost limits |

## Scope discipline

- Do not enumerate cloud metadata addresses, internal CIDRs, cluster services or adjacent tenants.
- Do not use recovered credentials outside the exact challenge component.
- SSRF redirects and DNS rebinding must be constrained to the assigned origin.
- Request smuggling/cache poisoning requires a dedicated challenge backend.
- Stop at a shared host/node/control plane; ask about that exact boundary.

## Common CTF patterns

- Over-permissive service account or mounted token.
- Public/versioned object storage with a previous secret.
- Container image layer containing a deleted secret.
- CI artifact or cache poisoning within the challenge's own pipeline.
- GraphQL field-level authz missing while the UI hides the field.
- API mass assignment or IDOR through a secondary identifier.
- Race between quota/credit check and resource creation.

## Verify

Prove the primitive with one read/write of a challenge-controlled object. The flag must come from the challenge component, not a shared secret. Record the exact request chain and least-privilege evidence.
