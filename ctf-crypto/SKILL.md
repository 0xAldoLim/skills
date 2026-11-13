---
name: ctf-crypto
description: "Solve CTF cryptography by modeling structure, oracles and implementation flaws. Use for RSA, ECC, discrete logs, lattices, PRNGs, stream/block ciphers, signatures, toy PQC, custom cryptosystems or mathematical puzzles. Reverse a compiled implementation before guessing the mathematics."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; Kali/Linux preferred, Windows/WSL for offline work. Tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-crypto

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Parse exact integers/bytes, equations, modulus/curve/group parameters and oracle behavior. Test invariants on supplied samples before querying remotely. Derive sample/query/compute costs and shrink the search space offline.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| RSA modulus/exponents, related ciphertexts or errors | GCD across samples, exact roots, modulus relationships, serializer threshold | [RSA](rsa-attacks.md), [recent oracles](modern-playbook.md) |
| ECB/CBC/AEAD, repeated nonce or padding | Compare blocks and actual encrypt/decrypt direction; authenticate a candidate plaintext | [Modes](modern-ciphers.md), [AEAD](modern-ciphers-4.md) |
| EC/DH signatures or malformed points | Validate order and point checks; nonce relations need the same key and precise equations | [ECC](ecc-attacks.md), [DH](dh-attacks.md) |
| LWE, HNP, Coppersmith, NTRU or PQC | Establish dimension, error bound, ring convention and measured leakage | [Lattices](lattice-and-lwe.md), [PQC](post-quantum.md) |
| Random state, hashes, stream cipher or ZKP | Count effective unknown bits; compare outputs/state updates and verifier constraints | [PRNG](prng.md), [stream](stream-ciphers.md), [ZKP](zkp-and-advanced.md) |
| Entirely custom algorithm or unusual algebra | Recover input/output length/alphabets, linearity, invariants, differentials and implementation bugs | [Custom systems](custom-systems.md) |

## Execute cheaply

Prefer Python stdlib exact integers, then `gmpy2`/`sympy`, then `fpylll`. Use Sage when polynomial, field, curve or isogeny operations materially reduce work; do not simulate them inaccurately to avoid a dependency. `../scripts/crypto_helpers.py` supplies tested exact roots, CRT, common-modulus recovery, parity-oracle intervals and bounded BSGS.

Budget oracles: count queries, derive the information per query, and stop when the remaining unknown bits cannot be resolved. For remote oracles, establish the baseline response and error behavior first. Reject folklore that a KEM, AEAD or large lattice is weak merely because it appears in a CTF.

When the implementation is opaque, pivot to [reverse](../ctf-reverse/SKILL.md) to recover the exact equations; keep crypto primary only while the mathematics is the blocker.

## Verify and finish

Reproduce the derivation in a clean script from the supplied parameters. Verify the flag with the challenge checker, a replayed plaintext/signature, or an authenticated response. A regex match is a candidate. Report the flag, the verification method and solver paths. Capture only understood, reproducible techniques via [learning](../docs/LEARNING.md); never store flags or keys.

## References

[INDEX.md](INDEX.md) for symptom routes and the full catalog. Load one to four matching sections only. [Personal learnings](personal-learnings.md), [detailed techniques](triage-reference.md), [2026 upstream additions](upstream-2026.md).
