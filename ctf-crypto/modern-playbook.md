# ctf-crypto modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## CBC decrypt used as encryption

**Signal / prerequisite:** The encryption routine calls CBC.decrypt; tail padding constrains plaintext.
**Cheapest useful test:** Draw the block dependency graph for two known blocks.
**Primitive and method:** Invert the implemented CBC relation from the constrained tail; verify reconstructed blocks with the exact mode/IV and padding.
**Failure / wasted work:** Standard encryption equations point in the wrong direction; missing tail constraints can leave ambiguity.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/ctf-gemastik/penyisihan-2024/blob/b5800ac9f044bd43056b3251fe1b51eb135969e4/crypto/baby-aes/writeup/README.md).

## RSA conversion overflow threshold oracle

**Signal / prerequisite:** Integer conversion allocates bit_length//8 bytes; exceptions differ.
**Cheapest useful test:** Encrypt known values on both sides of a byte boundary.
**Primitive and method:** Calibrate the actual exception predicate. Use multiplicative ciphertexts and exact modular interval intersections; re-encrypt the singleton.
**Failure / wasted work:** A canned error may still leak; naive binary search fails when modular products wrap.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; budgeted oracle transcript with exact integer intervals.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/ctf-gemastik/penyisihan-2024/blob/b5800ac9f044bd43056b3251fe1b51eb135969e4/crypto/broken-chall/writeup/README.md).

## Kyber decryption hash with sparse chosen messages

**Signal / prerequisite:** Raw decryption leaks hashes of low-entropy crafted messages, rather than an opaque KEM rejection.
**Cheapest useful test:** Derive one coefficient decision for the supplied codec and confirm a tiny local planted secret.
**Primitive and method:** Use carefully encoded ciphertexts to distinguish secret coefficients; bound hash-preimage work and integrate verified coefficient hints into the residual LWE problem.
**Failure / wasted work:** FO/implicit rejection, different compression or no low-entropy output can destroy the oracle. Standard ML-KEM is not automatically broken.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; offline precomputation, cached transcripts and verified lattice hints.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/f2797a33d8f5851508f37e854afceedf85eee8a3/crypto/kyber-decryption-oracle/solve/solv.sage).

## Uninitialized private exponent plus meet in the middle

**Signal / prerequisite:** Native big-integer key material includes attacker-shaped freed heap bytes.
**Cheapest useful test:** Compare successive public keys with local allocator traces.
**Primitive and method:** Reconstruct known key bytes and express the remaining exponent as a*L1+b*L2+c*B+d. Split the residual search into balanced tables and verify g^x equals the observed key.
**Failure / wasted work:** A leak depends on exact allocation sizes/endian order; generic DLP work misses the memory primitive.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; allocator trace then bounded MITM with measured RAM budget.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/crypto/cheap_logs/solve/solve.py).

## Unbalanced structured RSA factor roots

**Signal / prerequisite:** A decimal factor has known prefix/suffix and one bounded middle segment.
**Cheapest useful test:** Check gcd(scale,N) and estimate the smallest factor size.
**Primitive and method:** Build a monic base+scale*x polynomial. Set beta from the factor bound, X from the unknown segment; validate divisibility before decrypting.
**Failure / wasted work:** Fixed beta=0.5 can be unjustified for unbalanced factors. Sage exponent syntax differs from Python.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; Sage small_roots plus divisor/re-encryption assertions.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/uclaacm/lactf-archive/blob/3379d4a7b36680764a34e7dc817cc3c94c244764/2026/crypto/six-seven-again/solve.sage).

## Two-layer signed session and ECB cut-and-paste

**Signal / prerequisite:** Flask signing wraps an ECB-encrypted delimiter-separated role.
**Cheapest useful test:** Map both formats and a known username block boundary.
**Primitive and method:** Establish the independently justified signing-key weakness, then splice blocks from controlled registrations while preserving valid padding and role parsing. Verify each layer locally.
**Failure / wasted work:** Strong session signing, AEAD or unpredictable placement blocks the chain; bounded wordlist work needs evidence.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** medium; local cookie decode/sign and block-layout assertions.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://blog.androz2091.fr/en/insomnihack-25-unchained/).

## Repeated protocol shares defeat threshold secrecy

- **Signal:** An MPC protocol exposes evaluations of one low-degree secret polynomial through repeated participant registration.
- **Cheap test:** Identify field, degree, evaluation coordinates and whether registrations refer to the same polynomial.
- **Method:** Collect only the permitted distinct evaluations needed for interpolation; compute the constant term with exact field arithmetic and verify all observed shares.
- **Failure / pivot:** Per-session rerandomization, duplicate coordinates or a registration cap invalidate the shortcut. Do not infer an arbitrary smart-contract compromise.
- **Verification:** Evaluate the recovered polynomial against every original share and the protocol check. Source reviewed; challenge not locally reproduced.
- **Source:** [DeFiHackLabs; HITCON CTF 2024](https://github.com/DeFiHackLabs/hitcon-ctf-2024-writeup/blob/539fd42fe6adfaeabeacce8fa4a906785793a4f9/writeup/noexitroom.md)
