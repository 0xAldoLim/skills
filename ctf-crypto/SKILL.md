---
name: ctf-crypto
description: "Solve CTF cryptography using structural analysis, oracle modeling and implementation flaws. Use for RSA, symmetric modes, signatures, PRNGs, ECC, lattices or toy PQC; reverse compiled implementations before guessing the mathematics."
license: MIT
compatibility: Codex CLI on Kali Linux with Python 3 and terminal access; optional tools installed on demand.
metadata:
  user-invocable: "true"
---

# ctf-crypto

## Execute the solve

Read the description, inventory and identify supplied files, preserve originals, and search obvious flag candidates. Develop locally when source/binaries are available. Use normal solving operations autonomously within the assigned challenge.

**Scope:** the provided challenge instance is in scope; CTFd, scoreboard, provisioning, organizer networks, shared hosts/nodes, other teams and neighboring addresses are out of scope. Never probe, enumerate, fuzz, brute force or exploit competition infrastructure. A recovered URL/credential or reachable internal address does not add scope. Stop at a shared boundary; clarify only the exact boundary if an intended escape needs it. Read [scope](../docs/SCOPE.md) when network or escape behavior is involved.

**Remote health:** before deep remote work use a cheap DNS/TCP/TLS and baseline HTTP/protocol check. Generic 404/410, proxy 502/503/504, NXDOMAIN/refused/timeouts can mean expiry. Confirm with at most two small known-route/protocol tests; one 404 alone is inconclusive. If unavailable, stop remote exploitation, request a refreshed instance, preserve `solve/STATE.md`, and resume the existing solver after refresh. See [health](../docs/INSTANCE_HEALTH.md).

Open [INDEX.md](INDEX.md), then one to four references matching observed evidence. Track up to three strong hypotheses in normal mode; run their cheapest discriminating tests. Escalate local reasoning, mathematics, emulation and technical research for hard/zero-solve challenges. Budget expensive and remote experiments; prefer reduced offline search. Never expand target scope.

Search concepts, documentation, source and analogous techniques during live solves; do not search exact active challenge writeups/solutions/flags. Paths to helpers are relative to this skill/bundle, not the challenge directory. Use existing Kali CLI tools, stdlib and reliable packages first; install missing tools on demand with `../scripts/install_ctf_tools.sh`. Detailed [workflow](../docs/WORKFLOW.md) covers persistent state and human-assisted discriminators.

## Finish and learn

Verify the flag through a reproducible derivation or actual checker; a regex match is a candidate. Return flag, verification, short solution and solver paths. Only generate a full writeup when requested. After a verified solve, automatically capture materially useful, reproducible, understood, novel methods with `../scripts/capture_learning.py record.json --auto`. Check concepts and prerequisites, not titles alone; never store flags, passwords, live instance IDs, failures or luck. Promotion and index maintenance are in [learning](../docs/LEARNING.md). Never auto-push.

## Category triage

Parse exact integer/byte encodings, equations, modulus/curve/group parameters and oracle behavior. Test invariants on supplied samples before querying remotely. Derive sample/query/compute costs and shrink search spaces offline.

| Evidence | Cheap discriminator | Reference |
|---|---|---|
| RSA modulus/exponents, errors or related ciphertexts | GCD across samples, exact roots, modulus relationships, serializer threshold | [RSA](rsa-attacks.md), [recent oracles](modern-playbook.md) |
| ECB/CBC/AEAD, repeated nonce or padding | Compare blocks and actual encrypt/decrypt direction; authenticate candidate plaintext | [Modes](modern-ciphers.md), [AEAD](modern-ciphers-4.md) |
| EC/DH signatures or malformed points | Validate order and point checks; nonce relations need same key and precise equations | [ECC](ecc-attacks.md), [DH](dh-attacks.md) |
| LWE, HNP, Coppersmith, NTRU or PQC | Establish dimension, error bound, ring convention and measured leakage | [Lattices](lattice-and-lwe.md), [PQC](post-quantum.md) |
| Random state, hashes, stream cipher or ZKP | Count effective unknown bits; compare outputs/state updates and verifier constraints | [PRNG](prng.md), [stream](stream-ciphers.md), [ZKP](zkp-and-advanced.md) |

Prefer Python stdlib, PyCryptodome, sympy/gmpy2, then fpylll for actual lattice work. Use Sage when polynomial, field, curve or isogeny operations materially reduce work; do not simulate them inaccurately to avoid a dependency. `../scripts/crypto_helpers.py` supplies tested exact roots, generalized CRT, common-modulus recovery, parity-oracle intervals and bounded BSGS. Reject folklore that a KEM, AEAD, or large lattice is weak merely because it appears in a CTF.

- [Personal challenge-derived learnings](personal-learnings.md) — load matching sections only.
- [Detailed existing techniques](triage-reference.md) — load matching sections only.
- [Complementary upstream techniques](upstream-2026.md) — load matching sections only.
