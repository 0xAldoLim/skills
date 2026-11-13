# Custom and unfamiliar cryptosystems

Use this when the challenge implements its own cipher, encoding, key exchange, signature, hash or algebraic structure. Do not force it into a named primitive.

## Recover the interface

Write down:

- byte/word size, endianness, alphabet and padding;
- key/nonce/tag lengths and where each comes from;
- exact encrypt/decrypt direction and whether decryption is available;
- state size, round count and update order;
- what the oracle accepts and rejects, including errors and timing;
- any serialization (JSON, length prefix, base64, ASN.1) around the primitive.

Test one supplied sample end-to-end. A model that cannot reproduce a known ciphertext/plaintext pair is wrong.

## Classify the structure

| Observation | Hypothesis | Cheap test |
|---|---|---|
| Same plaintext positions change together | Block cipher or transposition | Flip one input bit; map changed output positions |
| One input bit changes many output bits globally | Diffusion/SPN or hash | Differential at reduced rounds |
| Output length = input length + constant | Stream cipher/encoding | XOR two ciphertexts with known relation |
| Additive/multiplicative relations hold | Linear algebra over a field/ring | Solve small linear system; check rank |
| Commutative diagram / homomorphism | Group/ring/lattice structure | Test `f(a*b)=f(a)*f(b)` on samples |
| Small state or short period | LFSR/PRNG/counter | Collect outputs, find recurrence/cycle |
| Verification only, no decryption | Signature/MAC/ZKP | Test malleability, replay, missing binding |

## Attack the implementation, not only the math

- key/nonce reuse, counter reset, truncation, endianness bugs;
- non-constant-time compare or early exit (timing oracle);
- unauthenticated encryption, missing associated-data binding, tag truncation;
- weak randomness, timestamp seeds, `rand()`/MT misuse;
- parser confusion between two representations;
- verifier that checks a different object than the one used;
- exception/error paths that leak state.

## Algebraic and oracle work

For a custom group/ring, write the operation table for a small parameter set and look for associativity, inverses, zero divisors and subgroup structure. For an oracle, derive the information per query before coding. For a custom hash, test length extension, padding collisions, state inversion and truncated output. For a custom signature, test nonce relations, missing message binding and public-key substitution.

Use Sage when field/curve/polynomial operations dominate; otherwise exact Python and `sympy` are cheaper. Use Z3 only when the constraints are finite and the model is validated on a known pair.

## Differential and linear analysis

Change one bit/byte at a time at the input and observe the output difference. At reduced rounds, look for a characteristic that survives to the full cipher with measurable bias. Validate the predicted bias on held-out samples before attempting key recovery. For linear cryptanalysis, test a mask relation on known plaintext/ciphertext pairs and estimate the correlation.

## Worked pattern: toy SPN

1. Reproduce the round function from source.
2. Disable the final key addition and encrypt a known plaintext.
3. Flip one S-box input bit; record the output difference.
4. Build the difference distribution table for the S-box.
5. Search a one- or two-round characteristic with high probability.
6. Extend to the full round count; collect enough pairs to distinguish the correct last-round key.
7. Verify the recovered key by decrypting a fresh ciphertext.

## Worked pattern: custom hash

If the compression function is invertible and the output is truncated, recover the internal state from enough outputs, then invert to the prefix. If the padding is ambiguous, test two messages that collide under the parser but not under the verifier. If the hash is used as a MAC with a secret prefix, test length extension.

## When to stop

If the model has more free parameters than observations, gather one more discriminating pair instead of adding assumptions. If two structural hypotheses predict the same observation, design a test that separates them. If the implementation is opaque, reverse the decisive routine before guessing the mathematics.
