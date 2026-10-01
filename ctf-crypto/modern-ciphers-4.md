# CTF Crypto - Modern Cipher Attacks (Part 4)

ChaCha20-Poly1305 nonce reuse (RFC 8439 $2^{130}-5$), partitioning-oracle / key-committing AEAD splitting via lattice, sponge generality (SHA-3 / Keccak / Ascon / Gimli / Sparkle) with rate/capacity/rounds/pad table and endianness workflow, and eSTREAM Trivium/Grain warmup + cube attack. For AES-GCM GHASH, see [modern-ciphers.md](modern-ciphers.md#aes-gcm-nonce-reuse--forbidden-attack); for sponge collisions and SHA-256 basis, see [modern-ciphers-3.md](modern-ciphers-3.md).

## Table of Contents
- [ChaCha20-Poly1305 Nonce Reuse — Forbidden Attack over $2^{130}-5$ (RFC 8439, picoCTF 2025)](#chacha20-poly1305-nonce-reuse--forbidden-attack-over-2130-5-rfc-8439-picoctf-2025)
- [Partitioning-Oracle / Key-Committing AEAD & Ciphertext Splitting via Lattice](#partitioning-oracle--key-committing-aead--ciphertext-splitting-via-lattice)
- [Sponge Construction Generality — SHA-3 / Keccak / Ascon / Gimli / Sparkle](#sponge-construction-generality--sha-3--keccak--ascon--gimli--sparkle)
- [eSTREAM Trivium (1152-round Warmup) & Grain — Cube Attack Outline](#estream-trivium-1152-round-warmup--grain--cube-attack-outline)

---

## ChaCha20-Poly1305 Nonce Reuse — Forbidden Attack over $2^{130}-5$ (RFC 8439, picoCTF 2025)

Same key/nonce reuses the encryption stream and one-time MAC key. For authentication, distinguish the polynomial accumulator modulo p=2**130-5 from the final 128-bit serialized tag; the imported recipe conflated them. Build RFC AEAD data from padded AAD, padded ciphertext and little-endian 64-bit lengths. Raw Poly1305 appends the block's high one bit, including partial raw blocks. The local diagnostic `scripts/poly1305_helper.py` is tested against the RFC vector; it is not a production constant-time implementation.

For two transcripts, enumerate the small integer carry difference k in -4..4 and solve `P1(r)-P2(r) = T1-T2+k*2**128 (mod p)`. Filter r by its clamp mask, recover `s=(T1-P1(r)) mod 2**128`, and verify every known tag with final 128-bit reduction. Keep all surviving candidates until another transcript distinguishes them. A field root alone does not prove the key. This corrects the omitted tag truncation, AEAD padding/length encoding and unsupported root-filter shortcut.

Recover plaintext only where a known plaintext exposes stream bytes. Authentication forgery does not reveal unknown plaintext. [RFC 8439](https://www.rfc-editor.org/rfc/rfc8439) specifies serialization; perform a planted local reproduction before spending instance queries.

## Partitioning-Oracle / Key-Committing AEAD & Ciphertext Splitting via Lattice

Signal: a password-derived-key endpoint distinguishes authentication outcomes. Establish the exact scheme, candidate derivation, nonce, AAD, tag length and error predicate using local known keys. A partitioning ciphertext must be one identical ciphertext/tag accepted by a chosen subset of candidate keys; merely generating a different ciphertext or tag for each key is not a partitioning oracle.

For suitable noncommitting GCM constructions, derive the actual multi-key GHASH equations and solve the field-linear interpolation system, retaining the exact length block, nonce mask and common tag. Verify acceptance under every intended candidate and rejection under the complement before using one bounded challenge query. Choose subsets to reduce the remaining candidate space. Scheme-specific requirements, message-size limits and oracle noise can make a construction infeasible; analyze those before expensive work.

The imported integer-lattice demo used unrelated truncated-tag bytes and a tautological equality; it did not construct or verify a colliding ciphertext. It is removed. Neither putting H(key) in AAD nor using a named misuse-resistant mode automatically proves key commitment. Use the precise definition and construction in [Partitioning Oracle Attacks](https://www.usenix.org/conference/usenixsecurity21/presentation/len), rather than a generic LLL/BDD recipe.

## Sponge Construction Generality — SHA-3 / Keccak / Ascon / Gimli / Sparkle

**Sponge:** state $= rate (r) + capacity (c)$, permutation $f$ (e.g., Keccak-$f[1600]$), pad `10*1` ($0x06$ for SHA-3, $0x01$ for raw Keccak), squeeze. Security $\approx \min(c/2, \text{output})$. Lightweight variants keep same sponge but swap $f$.

| Primitive | State | Rate $r$ | Capacity $c$ | Rounds | Padding | Endianness | Notes |
|-----------|-------|----------|--------------|--------|---------|------------|-------|
| SHA3-256 (FIPS-202) | 1600 | 1088 | 512 | 24 ($\text{Keccak-}f$) | `0x06` + `0x80` | LE lanes | NIST; $0x06$ = `01` + `10*1` |
| Keccak-256 (pre-NIST) | 1600 | 1088 | 512 | 24 | `0x01` + `0x80` | LE lanes | Ethereum `keccak256`; **0x01 vs 0x06** break |
| Ascon-128 / Ascon-128a (CAESAR/NIST LWC) | 320 | 64 / 128 | 256 / 192 | 12 (init/final) + 6/8 (bulk) | `0x80…0` (`1` + zeros) | BE bytes | $p^a=12$, $p^b=6$ (128) or $8$ (128a) |
| Ascon-Hash-256 | 320 | 64 | 256 | 12 | `0x80…0` | BE | Same perm, hash mode |
| Gimli (NIST LWC finalist) | 384 | 128 (r=16B) | 256 | 24 (SP-box) | `0x1F…0x80` (frame bits) | LE words | $f=384$, 6 SP-box rounds $\times 4$ |
| Sparkle-256 / Esch256 (SPARKLE) | 384 (6$\times$64) | 256 (Esch) | 128 | 10 (big) / 7 (slim) | `0x1F` domain sep | LE limbs | ARX, $2^{130}-$like? capacity $c=128$ |

**Padding distinction (critical for offline hash):**

| Hash | Pad bytes | Effect |
|------|-----------|--------|
| SHA3 (FIPS-202) | `0x06 || 0x00* || 0x80` | `...0110` + pad10*1 |
| Keccak (pre-NIST) | `0x01 || 0x00* || 0x80` | `...0001` + pad10*1 |
| Ascon | `0x80 || 0x00*` | single `1` + zeros |
| Gimli/Esch | `0x1F || ... || 0x80` | domain separation |

Mixing `0x06` vs `0x01` produces completely different digests — common CTF bug when solver uses Python `hashlib.sha3_256` (FIPS) against a challenge using raw `keccak`.

```python
# Sponge generality — FIPS SHA3 vs Keccak, Ascon/Gimli endianness workflow
# pip install pycryptodome sha3  (hashlib primary, galois/sympy unnecessary here)
import hashlib

def sha3_vs_keccak(msg: bytes):
    # Primary: hashlib (FIPS SHA3) + pysha3 / pycryptodome Keccak (raw)
    fips = hashlib.sha3_256(msg).hexdigest()
    try:
        from Crypto.Hash import keccak
        raw = keccak.new(digest_bits=256)
        raw.update(msg)
        keccak_hex = raw.hexdigest()
    except ImportError:
        import sha3  # pysha3
        keccak_hex = sha3.keccak_256(msg).hexdigest()
    return fips, keccak_hex

# Endianness workflow for offline sponge reimplementation
def le_lane(x: int) -> bytes:
    return x.to_bytes(8, 'little')

def be_lane(x: int) -> bytes:
    return x.to_bytes(8, 'big')

# Keccak state is 5x5 lanes LE; Ascon is 5 x 64-bit BE words; Gimli is 3x128 LE columns
# When reimplementing, match challenge's lane order:
#  - Keccak/SHA3: lanes are x + 5*y indexed LE
#  - Ascon: state words x0..x4 as BE uint64 (cipher spec)
#  - Gimli: columns as LE uint32 triples
# Example: absorb one block
fips, raw = sha3_vs_keccak(b"abc")
assert fips != raw  # 0x06 vs 0x01 matters
print(f"SHA3-256('abc')={fips}")
print(f"Keccak-256('abc')={raw}")
```

<details><summary>Sympy / manual fallback (padding illustration)</summary>

```python
# Manual Keccak pad10*1 illustration (no library)
def pad101(rate_bytes: int, msg_len: int, suffix: int) -> bytes:
    # FIPS suffix 0x06, Keccak 0x01, Ascon 0x80, Sparkle 0x1F
    pad = bytearray()
    pad.append(suffix)
    # ... zero bytes ...
    # final byte OR 0x80
    return bytes(pad)

# Sage not needed; for matrix reasoning about sponge linear layer use sympy GF(2) as in modern-ciphers.md
from sympy import Matrix
M = Matrix([[1,1,0],[0,1,1],[1,0,1]])  # toy diffusion matrix
print(M.rref(iszerofunc=lambda x: x%2==0))
```

</details>

**Offline sponge workflow (generic):**

1. Identify $f$ by constants: `Keccak-f[1600]` RC = `0x0000000000000001...`, Ascon RC = `0xf0..`, Gimli SP-box = `x^3` pattern, Sparkle ARX `0x9e3779b9`.
2. Handle endianness: read spec — Keccak/Gimli are LE lanes/words, Ascon/Esch are BE words. Swapping silently breaks tests.
3. Apply correct suffix/pad (`0x06` vs `0x01` is the #1 interop bug).
4. Absorb $r$-bit blocks, permute $f$ each block, squeeze $output$ bits.

**References:** FIPS 202, Bertoni et al. *Sponge & Duplex Constructions* (2007), NIST LWC *Ascon* (2021), Bernstein et al. *Gimli*, Beierle et al. *Sparkle*.

---

## eSTREAM Trivium (1152-round Warmup) & Grain — Cube Attack Outline

**Trivium (eSTREAM finalist):** 288-bit state = 93 + 84 + 111 bit registers $(s_1,s_2,s_3)$. Key 80-bit + IV 80-bit loaded into state, then **1152 warmup rounds** ($4 \times 288$) with no output. Each round updates:

```
t1 = s66  ^ s91 & s92 ^ s93 ^ s171
t2 = s162 ^ s175& s176^ s177^ s264
t3 = s243 ^ s286& s287^ s288^ s69
(s1,s2,s3) <<=1; s93=t3; s177=t2; s288=t1
```

Keystream is $s66\oplus s93\oplus s162\oplus s177\oplus s243\oplus s288$ after warmup.

**Grain v1 / Grain-128a:** LFSR + NFSR (80+80 or 128+128), 160/256 warmup rounds, filter $h$, output $z = h(x) \oplus s_{...}$.

**Cube attack (Dinur–Shamir, ASIACRYPT 2009):** Treat Trivium as degree-$d$ polynomial $p(k_0..k_{79}, v_0..v_{79})$ with cube variables $v$ (public IV bits) and superpoly in secret key bits $k$.

1. **Preprocessing (offline, same IV structure):** For each cube $C \subseteq \{v_i\}$, sum $p$ over $2^{|C|}$ assignments of $C$ → superpoly $p_C(k)$.
2. For reduced-round Trivium ($<1152$ rounds) many $p_C$ become **linear** in $k$. Detect linearity via BLR test. Keep those cubes.
3. **Online:** Query oracle $2^{|C|}$ times per cube, compute sums → right-hand side of linear equations in $k$.
4. Solve linear system over $GF(2)$ (Gaussian elimination) for key bits. Remaining bits brute-force.

```python
# Trivium 1152 warmup + toy cube attack demo over GF(2)
# pip install galois  (primary), sympy fallback in <details>

def trivium_keystream(key_bits: list[int], iv_bits: list[int], n_bits: int = 128) -> list[int]:
    # Registers s[0..287] (1-indexed in spec)
    s = [0]*288
    for i in range(80): s[i] = key_bits[i]
    for i in range(80): s[93+i] = iv_bits[i]
    # s[93+80..] and tail constants (spec: s[285]=1,s[286]=1,s[287]=1)
    s[285]=s[286]=s[287]=1
    # Warmup 1152 = 4*288 rounds
    for _ in range(4*288):
        t1 = s[65] ^ (s[90] & s[91]) ^ s[92] ^ s[170]
        t2 = s[161] ^ (s[174] & s[175]) ^ s[176] ^ s[263]
        t3 = s[242] ^ (s[285] & s[286]) ^ s[287] ^ s[68]
        s = [t3] + s[:92] + [t1] + s[93:176] + [t2] + s[177:287]
        # simplified rotate; real uses shift registers with taps above
    out = []
    for _ in range(n_bits):
        out_bit = s[65] ^ s[92] ^ s[161] ^ s[176] ^ s[242] ^ s[287]
        out.append(out_bit)
        t1 = s[65] ^ (s[90] & s[91]) ^ s[92] ^ s[170]
        t2 = s[161] ^ (s[174] & s[175]) ^ s[176] ^ s[263]
        t3 = s[242] ^ (s[285] & s[286]) ^ s[287] ^ s[68]
        s = [t3] + s[:92] + [t1] + s[93:176] + [t2] + s[177:287]
    return out

# Toy cube attack: reduced-round Trivium (e.g., 700 rounds) with cube {iv0, iv1}
# Sum over cube assignments -> linear superpoly in key bits
def cube_sum(trivium_fn, key_bits, cube_vars: list[int], fixed_iv: list[int]) -> int:
    # cube_vars are indices of IV bits to vary
    total = 0
    for mask in range(1 << len(cube_vars)):
        iv = fixed_iv[:]
        for j, idx in enumerate(cube_vars):
            iv[idx] = (mask >> j) & 1
        total ^= trivium_fn(key_bits, iv, n_bits=1)[0]
    return total

# Example: with reduced warmup (say 2*288) the superpoly for cube {1,2} becomes key[0] ^ key[5]
# Collect many such equations and solve with galois/GF(2)
try:
    import galois
    GF2 = galois.GF(2)
    # Linear system A*k = b over GF(2)
    # Toy: 3 equations in 4 key bits
    A = GF2([[1,0,0,1],[1,1,0,0],[0,1,1,0]])
    b = GF2([1,0,1])
    # Solve via Gaussian elimination (galois does rref)
    # Augmented matrix
    aug = GF2([[1,0,0,1,1],[1,1,0,0,0],[0,1,1,0,1]])
    print("GF(2) toy cube system rref:", aug.row_reduce())
except ImportError:
    pass
```

<details><summary>Sympy fallback (no galois)</summary>

```python
from sympy import Matrix

# Same Trivium warmup as above (copy trivium_keystream)

# Cube sum brute-force as above
# Linear solve over GF(2) via sympy rref(iszerofunc=lambda x: x%2==0)
A = Matrix([[1,0,0,1],[1,1,0,0],[0,1,1,0]])
b = Matrix([1,0,1])
aug = A.row_join(b)
rref, pivots = aug.rref(iszerofunc=lambda x: x % 2 == 0, simplify=True)
# Reduce mod 2
rref_mod2 = rref.applyfunc(lambda x: x % 2)
print(rref_mod2)
# Sage alternative:
# from sage.all import GF, matrix
# A = matrix(GF(2), [[1,0,0,1],[1,1,0,0],[0,1,1,0]])
# b = vector(GF(2), [1,0,1])
# A.solve_right(b)
```

</details>

**Practical notes:** Full 1152-round Trivium resists cubes up to ~30. CTFs use **reduced warmup** (e.g., 288 or 576 rounds) or leak many keystream bits — then cubes of size 10–20 yield linear superpolys. Grain with small $h$ degree behaves similarly: choose cube bits from IV/LFSR positions feeding low-degree monomials. Always check warmup parameter first — `4*state_size` signals the standard; anything smaller is the attack surface.

**References:** De Cannière–Preneel *Trivium* (eSTREAM 2006), Dinur–Shamir *Cube Attacks on Tweakable Black Box Polynomials* (2009), Liu et al. *Cube Attack on Reduced Trivium* (2018).

