# Post-quantum challenge discrimination

## ML-KEM / Kyber implementation oracle

First distinguish raw PKE decryption, deliberately weakened Kyber, and standardized ML-KEM. Record exact dimensions, modulus, noise distributions, codec/compression, ciphertext validation and observable output. The [FIPS 203 specification](https://csrc.nist.gov/pubs/fips/203/final) defines ML-KEM with its own encapsulation/decapsulation checks; a raw-decryption CTF oracle does not establish an attack against standard ML-KEM. Calibrate one chosen ciphertext against a tiny planted secret before collecting expensive data. Preserve coefficient ordering and NTT conventions. Follow the [reviewed DUCTF oracle variant](modern-playbook.md) only if its leakage exists.

## LWE and module lattices

Write the actual relation `b = A*s + e mod q`. Establish matrix orientation, secret/error bounds and centered representatives. Use fpylll for ordinary integer lattice reduction when its native dependencies are available; Sage helps with polynomial/module arithmetic. For small toy dimensions, enumerate a bounded secret to verify the model before a CVP/embedding attempt. Confirm every recovered candidate by computing the original residuals, not by assuming the first short vector is the secret. Lattice estimators forecast work, not solve samples; inspect the installed estimator API and pass a parameter object appropriate to that revision. Never paste an unverified keyword signature or claim `m > 2n` guarantees recovery.

## NTRU and related constructions

Identify the ring and convolution exactly: cyclic, negacyclic and quotient-ring multiplication differ. Verify a tiny polynomial multiplication against the implementation. Balance the public-key lattice blocks according to secret/noise sizes, then test any short candidate against the key relation and invertibility requirements. Do not label Kyber as NTRU or assume a common coefficient flattening is sufficient.

## SIDH / CSIDH / generic isogenies

Identify auxiliary torsion images, field, curve and action before choosing an attack. Broken SIDH-style key exchange, CSIDH class-group action, and ordinary isogeny-volcano walks have different prerequisites. A smooth p+1 alone is not a SIDH detector. For a challenge-specific proof/protocol, inspect its validation and degree constraints before attempting a full cryptanalytic implementation. Heavy Sage/isogeny tooling is a late step after those cheap discriminators.

Verification: operational discriminators reviewed; no promise that arbitrary PQC parameters are tractable. Preserve evidence and pivot toward codec, oracle, validation or protocol flaws when no feasible mathematical bound exists.
