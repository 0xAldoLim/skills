# Personal verified challenge learnings

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-19

- **Python `random.seed(bytes)` v2 sparse seed recovery:** Do not default to 624-output MT cloning when the original seed is a short byte string. For 8-byte seeds, carefully aligned outputs around indices `3..6` and `230..233` can recover the original bytes, then candidate seeds should be replayed locally against the observed prefix before using predictions.
- **AES without `SubBytes` becomes affine:** If a challenge disables `SubBytes` but still gives an encryption oracle, model the block cipher as `E(x) = L(x) xor b`. Query `E(0)` plus encryptions of basis blocks, recover the linear map over GF(2), and solve for protected plaintexts directly.
- **Bounded-error mod-`q` basis-error reduction:** For overdetermined modular systems where the secret is large but the equation errors are small, choose an invertible row basis, move the uncertainty into a smaller basis-error vector, then attack that reduced congruence with an embedding lattice before touching the original secret directly.
- **Decorative signature wrapper plus real MAC:** In hybrid web/crypto auth challenges, treat fake or user-visible signature objects as potential leakage channels for secret material reused by a stronger verifier. Confirm what each verifier really checks, and whether canonical serialized secret material is hashed into an HMAC or secondary token signer.
- **Noisy monoalphabetic substitution:** If IC still indicates monoalphabetic substitution but the best plaintext has isolated nonsense letters, keep the recovered key and treat the remaining errors as sparse channel noise. Rebuild the n-gram scorer for the real language and finish with context-aware correction instead of restarting the solve from scratch.
- **Toy Ring-LWE factor saturation:** When a small-field RLWE instance factorizes nicely, test whether each factor-coordinate image of the claimed small-coefficient distribution already saturates the base field. If it does, factorwise MITM will not prune the secret directly, so shift effort toward protocol flaws, deterministic public-only derivations, or transcript incompleteness.

