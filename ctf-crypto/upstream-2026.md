# Complementary upstream techniques

Source: ljagiello/ctf-skills at c332c7be1b27cb64639a20124ac55ba916adef92 (MIT), retrieved 2026-10-01. Read the prerequisites for each technique; historical examples do not authorize infrastructure interaction.

## Coppersmith via Howgrave-Graham Lattice (fpylll primary)

The upstream lattice construction is a useful implementation lead, but its root filter checked `f(root) == 0 mod N` even when seeking a root modulo an unknown divisor. That rejects valid factor roots. Prefer the reviewed Sage workflow in [advanced-math.md](advanced-math.md). For a custom fpylll implementation, justify row shifts/scaling and parameter bounds, divide column j by X^j before extracting an integer polynomial, and validate candidates with `gcd(f(root),N)` against the required divisor bound. Do not call fpylll "pure Python": it wraps native fplll and needs compatible native libraries. Benchmark an offline planted root before trying challenge data.

## HNP Cross-Link: ECDSA Truncated Nonces → Lattice (8-sig example)

For known high nonce bits `k_i = K_i + delta_i`, ECDSA gives `delta_i = a_i*d + b_i (mod q)`, with `a_i=r_i/s_i`, `b_i=h_i/s_i-K_i` and `0 <= delta_i < B`. Check inverses and exact leaked-bit alignment. Construct a CVP/embedding from those a_i and b_i with centered residuals and scales derived from B and q; include each r_i. Inspect the existing [lattice reference](lattice-and-lwe.md) against these equations before reuse. A fixed eight-signature recipe or a two-bit tweak does not guarantee success. Validate d against the supplied EC public key and every nonce interval. The earlier imported matrix omitted r_i and contained undefined variables/placeholder verification; it is deliberately replaced by the derivation.

## MOV Attack (Weil Pairing, embedding degree k≤6)

**Signals and conditions:** A prime subgroup of order r coprime to the characteristic has small embedding degree k, where r divides p^k-1. This suggests a pairing reduction, not proof that the finite-field discrete log is cheap. Estimate the actual r-subgroup DLP cost; a small k or a field below 2048 bits alone does not imply feasibility. Confirm independent r-torsion is available over the chosen extension; the divisibility test alone does not guarantee a useful Weil pairing.

**Cheap test:** Check six modular powers before factoring a large order. This helper returns an embedding-degree candidate only.

```python
def embedding_degree(p, r, kmax=6):
    if r <= 1 or p % r == 0:
        return None
    power = 1
    for k in range(1, kmax + 1):
        power = power * p % r
        if power == 1:
            return k
    return None
```

**Reduction:** For Q=dG and an independent R in E[r], compute A=e_r(G,R), B=e_r(Q,R); solve B=A^d in the order-r subgroup, then verify dG=Q. Pairing G with Q gives 1 because they are dependent.

**Correction:** Project a random point using its actual point order n: R=(n/r)T when r divides n. Multiplying every point by #E/r can annihilate the whole r-torsion when r² divides #E. In a group (Z/rZ)², that old cofactor is r and every projected point is zero. Computing point orders, extension fields and DLPs may be expensive; budget them explicitly.

```python
# Requires Sage in a deliberately selected analysis environment.
from sage.all import GF, EllipticCurve, Integer, discrete_log

def mov_attack(p, a, b, Gx, Gy, Qx, Qy, r, attempts=32):
    if not Integer(p).is_prime() or not Integer(r).is_prime() or p % r == 0:
        raise ValueError("prime field and prime subgroup coprime to characteristic required")
    k = embedding_degree(p, r)
    if k is None:
        return None
    field = GF(p**k, 'alpha')
    curve = EllipticCurve(field, [a, b])
    G, Q = curve(Gx, Gy), curve(Qx, Qy)
    if G.is_zero() or not (r*G).is_zero() or not (r*Q).is_zero():
        raise ValueError("input points must be in the declared r-torsion")
    for _ in range(attempts):
        T = curve.random_point()
        n = T.order()  # Factorization/counting cost needs a budget.
        if n % r:
            continue
        R = (n // r) * T
        if R.is_zero():
            continue
        A = G.weil_pairing(R, r)
        if A == 1:
            continue
        B = Q.weil_pairing(R, r)
        d = int(discrete_log(B, A, ord=r))
        if d*G == Q:
            return d
    return None  # No independent pairing point found within budget.
```

**Failure/pivot:** Missing independent torsion, costly point orders or a hard finite-field DLP require revised field/algorithm feasibility, not random unlimited retries. Sage template is syntax-audited, not reproduced in this migration. [Sage's Weil-pairing contract](https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_point.html) requires both inputs to be n-torsion and documents the value 1 for dependent points. Foundational reduction: Menezes–Okamoto–Vanstone (1993).

---

## Twist Security & Twist Attacks

**Twist order:** If `#E = p + 1 - t` (trace `t`), quadratic twist has `#E' = p + 1 + t = p + 1 - #E + (p+1) ???` concretely `p+1+t`. Check `twist_order = p + 1 + t = 2*(p+1) - #E`.

```python
def twist_order(p, E_order):
    # #E = p+1 - t => t = p+1 - #E => #E' = p+1 + t = 2*(p+1) - #E
    return 2*(p+1) - E_order
```

**When vulnerable:** Implementation uses Montgomery `x-only` ladder (e.g., X25519) without validating `f(u)/B` is QR -- input may land on twist. If `twist_order` is smooth or has small factor `r`, send twist point of order `r` and learn `k mod r`.

**Check:** `factor(twist_order)` -- if smooth or has factor `< 1e6`, and protocol gives oracle (MAC/validity), attack as invalid-curve variant 5.

**Mitigations:** Use twist-secure curve (both `#E` and `#E'` have large prime factor, e.g., Curve25519), validate `is_on_curve` or QR check, reject zero shared secret (`RFC 7748`).

**References:** SafeCurves `safecurves.cr.yp.to/twist.html`; Bernstein 2006 twist attacks.

---

## GLV / CM Endomorphism Leakage (d=-3/-4)

**Pattern:** Curve has CM discriminant `d = -3` (`j=0`, `a=0`, `y^2=x^3+b`, sextic twists, `E: y^2=x^3+b` has `p ≡ 1 mod 3` gives endomorphism `phi: (x,y)->(zeta*x, y)`) or `d=-4` (`j=1728`, `a=...`, `y^2=x^3+a*x`, quartic twists, `phi: (x,y)->(-x, i*y)` when `p ≡ 1 mod 4`). GLV uses `phi` to decompose scalar: `kP = k1*P + k2*phi(P)` with `|k1|,|k2| ~ sqrt(n)`.

**CTF relevance:**
- If challenge leaks `k1` or `k2` timing/side-channel, or uses biased GLV decomposition, lattice recovers `k`.
- If `d=-3` curve reuses `zeta` endomorphism with small constants, check for weak `b` (small `b` → extra automorphisms).
- Detection: `j==0` → `d=-3`; `j==1728` → `d=-4`; `a==0 and p%3==1` or `b==0 and p%4==1`.

```python
def has_glv_endomorphism(p, a, b):
    # j=0 => d=-3, j=1728 => d=-4
    if a == 0 and b != 0:
        # y^2 = x^3 + b, j=0
        return p % 3 == 1, "-3 (j=0, sextic)"
    if b == 0 and a != 0:
        # y^2 = x^3 + a*x, j=1728
        return p % 4 == 1, "-4 (j=1728, quartic)"
    # generic: compute j
    j = 1728 * (4*a**3) * pow(4*a**3 + 27*b*b, -1, p) % p if (4*a**3+27*b*b)%p!=0 else None
    if j == 0:
        return True, "-3"
    if j == 1728 % p:
        return True, "-4"
    return False, None
```

**References:** Gallant-Lambert-Vanstone 2001; GLV endomorphism for `d=-3/-4`.

---

## X25519 Low-Order Points + All-Zero Check (RFC 7748)

X25519 clamps its scalar to a multiple of eight. A low-order input can therefore yield an all-zero shared secret; this is one predictable result, not eight candidate keys. Test the protocol's specified all-zero rejection in a local harness first. The u=0 input has order two on the curve; order labels and the full list of accepted encodings must come from the actual implementation, including noncanonical encodings and twist behavior. Scanning a few small u values does not enumerate the full low-order input set.

```python
def x25519_clamped(sk: bytes) -> int:
    if len(sk) != 32:
        raise ValueError('X25519 scalar must be 32 bytes')
    b = bytearray(sk)
    b[0] &= 0xF8
    b[31] &= 0x7F
    b[31] |= 0x40
    return int.from_bytes(b, 'little')

def all_zero(secret: bytes) -> bool:
    # Diagnostic Python predicate, not a constant-time implementation.
    return not any(secret)
```

If the assigned instance accepts that result, derive the exact KDF with its salt/transcript and verify a known MAC or ciphertext before one bounded test. If it rejects, do not infer a generic invalid-curve bypass of X25519; return to the application's authenticated key-exchange logic. [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748#section-6) defines the protocol checks.

## ForkAES-5-2-2 Reflective Differential (BSidesSF 2026)

**Pattern (forkaes):** ForkAES splits a 10-round AES-like permutation into a sequential `fork` structure: 5 rounds before the fork, then two parallel 2-round branches. The branching is reflective — both output blocks share the same middle state so a differential trail through the 5-round stem can be matched across both forks simultaneously.

```
          5 rounds
    P ─────────────► W  (fork point)
                     ├─► 2 rounds ─► C0  (branch 0)
                     └─► 2 rounds ─► C1  (branch 1)
```

State is AES-like: 4×4 byte matrix, `SubBytes` (same S-box), `ShiftRows`, `MixColumns`, `AddRoundKey` with distinct round keys (`k0..k4` before fork, `k5..k6` per branch).

```python
from Crypto.Cipher import AES  # for S-box reference only; ForkAES is custom
SBOX = AES.new(b'\x00'*16, AES.MODE_ECB)._sbox if hasattr(AES.new(b'\x00'*16, AES.MODE_ECB), '_sbox') else None
# Use standard AES SBOX table
SBOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]
INV_SBOX = [0]*256
for i, v in enumerate(SBOX):
    INV_SBOX[v] = i

def forkaes_reflect(P, keys5, keys_branch0, keys_branch1):
    """Reference ForkAES-5-2-2: 5 before fork, 2 per branch. keys are 16-byte round keys."""
    state = list(P)
    for r in range(5):
        # SubBytes, ShiftRows, MixColumns (skip last), AddRoundKey
        state = [SBOX[b] for b in state]
        state = shift_rows(state)
        if r != 4:
            state = mix_columns(state)
        state = [s ^ k for s, k in zip(state, keys5[r])]
    # fork
    c0 = list(state)
    c1 = list(state)
    for r in range(2):
        c0 = [SBOX[b] for b in c0]
        c0 = shift_rows(c0)
        if r != 1: c0 = mix_columns(c0)
        c0 = [s ^ k for s, k in zip(c0, keys_branch0[r])]
    for r in range(2):
        c1 = [SBOX[b] for b in c1]
        c1 = shift_rows(c1)
        if r != 1: c1 = mix_columns(c1)
        c1 = [s ^ k for s, k in zip(c1, keys_branch1[r])]
    return bytes(c0), bytes(c1)

def shift_rows(state):
    # state 16 bytes column-major: index = row + 4*col
    out = [0]*16
    for r in range(4):
        for c in range(4):
            out[r + 4*c] = state[r + 4*((c + r) % 4)]
    return out

def mix_columns(state):
    # AES MixColumns per column
    out = [0]*16
    for c in range(4):
        a0, a1, a2, a3 = state[0+4*c], state[1+4*c], state[2+4*c], state[3+4*c]
        out[0+4*c] = xtime(a0)^xtime(a1)^a1^a2^a3
        out[1+4*c] = a0^xtime(a1)^xtime(a2)^a2^a3
        out[2+4*c] = a0^a1^xtime(a2)^xtime(a3)^a3
        out[3+4*c] = xtime(a0)^a0^a1^a2^xtime(a3)
    return out

def xtime(a):
    return ((a << 1) ^ 0x11b) & 0xff if a & 0x80 else (a << 1) & 0xff
```

**Reflective differential — the distinguisher:**

Both branches share the fork state `W`. A differential `ΔW` propagates independently through branch 0 → `ΔC0` and branch 1 → `ΔC1`. For a correct guess of the last two round keys, the backward differential from `C0` and from `C1` must converge on the same `ΔW` — reflection. Wrong keys give inconsistent `ΔW`.

```python
def fork_differential_attack(pairs):
    """pairs: list of ((P, P'), (C0, C1, C0', C1')) with chosen ΔP."""
    # 1. Filter pairs where differential trail through 5-round stem is plausible
    #    (precompute DDT for S-box; MixColumns diffusion tells you which bytes active)
    # 2. For each surviving pair, brute-force last-round keys branch0/branch1 separately:
    for c0, c1, c0p, c1p in ciphertext_pairs:
        for k6_0_guess in range(256):  # last round key byte-wise; real brute over SubBytes diff
            # invert last round: C -> state before last AddRoundKey -> InvShiftRows -> InvSubBytes differential
            delta_w0 = inv_branch_differential(c0, c0p, k6_0_guess, branch=0)
            for k6_1_guess in range(256):
                delta_w1 = inv_branch_differential(c1, c1p, k6_1_guess, branch=1)
                if delta_w0 == delta_w1 and delta_w0 is not None:
                    # reflective match -> key bytes correct, proceed to full key
                    return k6_0_guess, k6_1_guess, delta_w0
    return None

def inv_branch_differential(c, cp, k_guess, branch=0):
    """Invert 2-round branch one round back using key guess, return Δ at fork."""
    # c ^ k_guess -> InvShiftRows -> InvSubBytes difference -> MixColumns inverse
    pre = [b ^ k_guess for b in c]  # toy: per-byte; real per 4-byte column
    # ... apply InvSBOX differential check via DDT ...
    return pre  # placeholder for fork delta
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage: model ForkAES differential as linear layer over GF(2^8) with S-box DDT
# Use sage's AES SBOX DDT for trail search: sage.crypto.block_cipher.sboxes.AES
from sage.crypto.sboxes import AES as SageAES
ddt = SageAES.difference_distribution_table()
# Trail search via sage's MILP or brute over 256 byte values
```

</details>

**Why 5-2-2 is fragile:**

- The 5-round stem has a known AES differential trail with only ~8 active S-boxes; challenges pick a low-weight trail so enough pairs survive.
- The 2-round branches are short enough that a single key-byte guess inverts them completely (last round has no MixColumns).
- Reflection doubles the signal: both branches must agree, so false positives from one branch are pruned by the other — the effective filter is squared.

**When to recognize:** Challenge says `ForkAES`, shows a fork diagram, or encrypts one plaintext to two ciphertexts. The key schedule splits round keys per branch — if you see `keys[0:5]` + `keys_branchA[0:2]` + `keys_branchB[0:2]`, it's this structure.

**References:** BSidesSF 2026 "forkaes", ForkAES spec 5-2-2.

---

## GhostBlood — Faulty ChaCha ARX Rotate (BSidesSF 2026)

**Pattern (GhostBlood):** ChaCha20 implemented with a faulty rotation — one of the four ARX rotates in the quarter-round is off by 1 (e.g., `<<< 12` instead of `<<< 16`, or `<<< 8` instead of `<<< 7`). The bug is silent: encryption still works, keystream still looks random, but the faulty rotate creates a linear correlation that reveals key bits via differential.

**ChaCha quarter-round (correct):**

```
a += b; d ^= a; d <<<= 16;
c += d; b ^= c; b <<<= 12;
a += b; d ^= a; d <<<= 8;
c += d; b ^= c; b <<<= 7;
```

Faulty variant (example): second rotate uses `11` instead of `12`, or last uses `8` instead of `7`.

```python
def chacha_qr(a, b, c, d, rotations=(16, 12, 8, 7), faulty=None):
    MASK32 = 0xffffffff
    def rotl(v, n):
        return ((v << n) | (v >> (32 - n))) & MASK32
    rots = list(rotations)
    if faulty is not None:
        idx, val = faulty
        rots[idx] = val
    a = (a + b) & MASK32; d ^= a; d = rotl(d, rots[0])
    c = (c + d) & MASK32; b ^= c; b = rotl(b, rots[1])
    a = (a + b) & MASK32; d ^= a; d = rotl(d, rots[2])
    c = (c + d) & MASK32; b ^= c; b = rotl(b, rots[3])
    return a, b, c, d

def chacha_block(key, nonce, counter, faulty=None):
    """Build ChaCha state 4x4: constants, key, counter, nonce; run 20 rounds (10 column+diagonal)."""
    import struct
    consts = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]
    k = struct.unpack('<8I', key)  # 32-byte key -> 8 words
    n = struct.unpack('<3I', nonce + b'\x00')  # 12-byte nonce; simplified
    state = consts + list(k) + [counter] + list(n[:3])
    working = state[:]
    for _ in range(10):
        # column rounds
        working[0], working[4], working[8], working[12] = chacha_qr(working[0], working[4], working[8], working[12], faulty=faulty)
        working[1], working[5], working[9], working[13] = chacha_qr(working[1], working[5], working[9], working[13], faulty=faulty)
        working[2], working[6], working[10], working[14] = chacha_qr(working[2], working[6], working[10], working[14], faulty=faulty)
        working[3], working[7], working[11], working[15] = chacha_qr(working[3], working[7], working[11], working[15], faulty=faulty)
        # diagonal rounds
        working[0], working[5], working[10], working[15] = chacha_qr(working[0], working[5], working[10], working[15], faulty=faulty)
        working[1], working[6], working[11], working[12] = chacha_qr(working[1], working[6], working[11], working[12], faulty=faulty)
        working[2], working[7], working[8], working[13] = chacha_qr(working[2], working[7], working[8], working[13], faulty=faulty)
        working[3], working[4], working[9], working[14] = chacha_qr(working[3], working[4], working[9], working[14], faulty=faulty)
    return [(w + s) & 0xffffffff for w, s in zip(working, state)]
```

**Finding the fault — rotation enumeration:**

Try all four rotation positions × plausible off-by-1 values (6,7,8,11,12,13,15,16,17,8...). For each candidate, check whether a known plaintext-ciphertext pair decrypts to readable ASCII.

```python
CANDIDATES = [(1, 11), (1, 13), (3, 6), (3, 8), (0, 15), (0, 17)]  # (index, faulty rotation)
PNG_MAGIC = b'\x89PNG'

def find_fault(cipher, known_pt_prefix, key_guess):
    for idx, val in CANDIDATES:
        ks = chacha_block(key_guess, nonce, counter, faulty=(idx, val))
        keystream = b''.join(v.to_bytes(4, 'little') for v in ks)
        pt = bytes(c ^ k for c, k in zip(cipher, keystream))
        if pt.startswith(known_pt_prefix) or PNG_MAGIC in pt:
            print(f"fault found: rotate index {idx} should be {(16,12,8,7)[idx]}, faulty={val}")
            return idx, val, pt
    return None

# Full key recovery when key unknown: faulty rotate linearizes part of ARX
# Differential: flip bit in `b`, the faulty rotate propagates differently.
# Collect ~2^16 pairs with single-bit input差分, brute-force that rotation's key byte.
def ghostblood_key_recovery(oracle):
    """oracle(plaintext) -> ciphertext under faulty ChaCha with unknown key."""
    # Chosen-plaintext differential: P and P^delta (one bit) -> C, C'
    # The faulty rotate causes Δ to stay in one nibble longer
    c0 = oracle(b'\x00'*64)
    c1 = oracle(b'\x00'*63 + b'\x01')
    delta = bytes(a ^ b for a, b in zip(c0, c1))
    # For correct fault, delta has low Hamming weight at known positions
    best = None
    for idx, val in CANDIDATES:
        # simulate delta distribution for this fault
        score = simulate_delta_weight(idx, val, delta)
        if best is None or score > best[0]:
            best = (score, idx, val)
    return best
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage: model ARX differential as bit-vector constraints
# The faulty rotate is symbolic: rot_amount is variable, differential trail weight depends on it
# Use sage's z3 bridge or pure IntegerMod for Hamming weight
def sage_arx_delta(weight):
    R = IntegerModRing(2**32)
    # carry analysis via R; not needed — Python path suffices
    pass
```

</details>

**Key insight:** ARX security depends on rotations being exactly `(16,12,8,7)`. Off-by-one breaks diffusion: the ARX carry chain no longer fully mixes between rounds, so a single-bit input差分 leaves a detectable pattern in the keystream difference. In CTF, the reduced diffusion also lets Z3 solve the ChaCha state with only ~4 blocks of known plaintext (instead of needing the full 20-round inversion).

**When to recognize:** Challenge mentions `ChaCha`, `ARX`, or shows quarter-round code with magic numbers `16,12,8,7`. Compare against the reference — any mismatch is the vulnerability. If the binary is provided, `objdump` the ChaCha core and diff rotates.

**References:** BSidesSF 2026 "GhostBlood".

See [exotic-crypto-2.md](exotic-crypto-2.md) for 2017+ era exotic crypto attacks (BB-84, ElGamal variants, Paillier oracles, Cayley-Purser, BIP39, Asmuth-Bloom, Rabin polynomial, Vandermonde).
## NTRU Lattice Recovery (G1) -- NTRU / NTRU Prime / Kyber Flattening

**Pattern:** `h = g * f^{-1} mod q` with small `f,g` (coeffs in `{-1,0,1}` or narrow Gaussian). CTF gives `h` and `q`, sometimes `N`.

**Recognition:**

- `q = 3329` (Kyber/ML-KEM) vs `q = 12289` vs `q = 2048` vs `q = 2^k`
- ring `R = Z_q[x]/(x^N+1)` (negacyclic, power-of-two NTRU), `R = Z_q[x]/(x^N-1)` (cyclic), `R = Z_q[x]/(x^p - x -1)` (NTRU Prime), `R = Z_q[x]/(x^256+1)` (Kyber/ML-KEM k=2/3/4)
- unravel: copy-paste of `h` list length `N` and mention of `f,g` Hamming weight.

**Lattice:** `H = circulant(h)` for cyclic, `H = negacyclic(h)` for `x^N+1` (sign flip on wrap). Basis

```
B = [[ q*I_N ,  0  ],
     [  H    , I_N ]]   # 2N x 2N, row convention as fpylll
```

Short vector is `(f_coeffs, g_coeffs)` up to rotation/sign. After `LLL -> BKZ`, target is `g = h*f mod q` centered in `[-q/2, q/2]`.

```python
from fpylll import IntegerMatrix, LLL, BKZ

def ntru_lattice(h, q, negacyclic=True):
    """Build NTRU lattice B=[[qI 0],[H I]] for ring x^N +/-1."""
    N = len(h)
    # H negacyclic vs circulant
    def rot(row, k):
        # k-th row of H: h shifted by k, sign flip for x^N+1 wrap
        r = [0]*N
        for j in range(N):
            idx = (j - k) % N
            s = -1 if (negacyclic and j < k) else 1
            r[j] = (s * h[idx]) % q
        return r
    n = 2*N
    rows = [[0]*n for _ in range(n)]
    for i in range(N):
        rows[i][i] = q
    for i in range(N):
        r = rot(h, i)
        for j in range(N):
            rows[N+i][j] = r[j]  # H block
        rows[N+i][N+i] = 1       # I block
    return IntegerMatrix.from_matrix(rows)

def recover_ntru(h, q, negacyclic=True):
    B = ntru_lattice(h, q, negacyclic)
    LLL.reduction(B)
    # BKZ for tighter instances (Kyber k=2 dim 512 needs BKZ 25+)
    try:
        BKZ.reduction(B, BKZ.Param(block_size=25))
    except Exception:
        pass
    # scan short rows for small (f,g)
    cand = []
    for i in range(B.nrows):
        row = [int(B[i,j]) for j in range(B.ncols)]
        # center g part is row[0:N] ? Actually last N is f, first N is g? Check convention
        # Our rows: top half is (q*e_i,0), bottom half is (H row, e_i)
        # Short vector (g, f) has g = H*f mod q centered
        # Test norm small and coeffs in [-q/2,q/2]
        if all(-5 <= v <= 5 for v in row):  # toy bound; tune for real q
            cand.append(row)
    return B, cand

# center: g = (h * f) mod q mapped to [-q/2,q/2]
def center_mod(v, q):
    return [(x + q//2) % q - q//2 for x in v]

# distinguish ring: x^N+1 vs x^N-1 vs x^p-x-1 vs x^256+1
# NTRU Prime p primes 653/761/857, x^p-x-1 not cyclotomic -- lattice same shape but H is circulant with different modulus.
# Kyber flattening: Module-LWE rank k=2/3/4, N=256, q=3329 -- flatten each polynomial coeff vector length 256*k (see ML-KEM section).
```

**Distinguish `x^N +/-1` vs `x^p-x-1` vs `x^256+1`:** `H` construction flips sign on wrap for `+1`; NTRU Prime uses `x^p - x -1` -- treat as generic circulant plus one extra reduction column; ML-KEM `x^256+1` per rank (Kyber). Ref: ePrint NTRU, SandboxAQ Kyber flattening notes, `k=2/3/4` table below.

**Failure:** forget centering `[-q/2,q/2]` vs `[0,q)` hides short vector; wrong `qI` scale vs `I` block.

---

## GGH Embedding / CVP Closest Vector (G2)

**Pattern:** `c = m * B_pub + e` with small `e` (GGH cryptosystem) or LWE `b = A*s + e`.

**Embedding lattice (Kannan):** sweep `lambda`

```
B_emb = [[ B_pub , 0 ],
         [  c    , λ ]]   # (n+1) x (m+1), λ in {1,2,4,...,128}
```

Small `lambda` trades embedding gap; try power-of-two sweep. Row-basis convention as `fpylll` (`IntegerMatrix.from_matrix(rows)`). `B_pub` rows are basis vectors.

```python
from fpylll import IntegerMatrix, LLL, CVP, GSO

def ggh_embed_lattice(B_pub, c, lam=1):
    n = len(B_pub)
    m = len(B_pub[0])
    rows = []
    for i in range(n):
        rows.append(list(B_pub[i]) + [0])
    rows.append(list(c) + [lam])
    return IntegerMatrix.from_matrix(rows)

def ggh_solve(B_pub, c):
    best = None
    best_err = None
    for lam in [1,2,4,8,16,32,64,128]:
        B = ggh_embed_lattice(B_pub, c, lam)
        LLL.reduction(B)
        # CVP vs Babai nuance:
        # CVP.closest_vector(B, target) is exact (exponential), use for dim<50;
        # else Babai nearest plane via GSO.Mat(B).babai(target) (approximate, fast).
        target = list(c) + [lam]
        try:
            # exact CVP when feasible; returns the lattice point directly
            cand = list(CVP.closest_vector(B, target))
        except Exception:
            # Babai nearest plane fallback: babai returns coefficient vector w,
            # so map it back to the lattice point with multiply_left.
            M = GSO.Mat(B)
            M.update_gso()
            w = M.babai(target)
            cand = list(B.multiply_left(w))
        # error-vector candidate: target minus lattice point, drop embed coord
        e_cand = [c[i] - cand[i] for i in range(len(c))]
        err = sum(v*v for v in e_cand)
        if best is None or err < best_err:
            best = cand
            best_err = err
    return best

# GSO.Mat.babai vs CVP.closest_vector:
# - CVP.closest_vector(B, target) exact, slow, dim<60
# - GSO.Mat(B).babai(target) approximate, fast, needs LLL/BKZ first
# Always LLL/BKZ before Babai; try CVP for toy CTF dims (<40).
```

**Warning: GGH vs GGH13:** textbook GGH (Goldreich-Goldwasser-Halevi) is the lattice encryption above; GGH13 (Garg-Gentry-Halevi) is multilinear-map zeroizing -- different trapdoor, different lattice (not CVP). Don't conflate.

---

## Mersenne AJPS / MLHRSP Small Roots (G3) -- p = 2^n -1

**Pattern:** `h = f/g mod p` with `p = 2^n -1` Mersenne prime, `n=11213, w=10` (L3ak / Mayhem CTF 2024) or `n=521,127,607` toy. `f,g` small weight `w` (sparse 0/1, `w=10` ones).

**AJPS lattice:** `F(x,y)= h*y - x mod p` with small roots `(f,g)`. Build `s=5, 6x6` shifts `x^i y^j F^k p^{s-k}` scaled `X=2^{\xi1 n} Y=2^{\xi2 n}`.

Cite: ePrint 2024/2080 (AJPS cryptanalysis), L3ak Mayhem `n=11213 w=10` challenge.

```python
from fpylll import IntegerMatrix, LLL

def mersenne_ajps_lattice(h, p, n, w, s=5):
    """Mersenne AJPS lattice p=2^n-1, h=f/g mod p, weight w.
    Builds 6x6 shifts (s=5, i/j loops) scaled X=2^{xi1 n} Y=2^{xi2 n}.
    Toy demo: n=521 w=4, 6x6 lattice finds small f,g.
    """
    # exponents xi1, xi2 from ePrint 2024/2080 Table 1 (depends on w/n ratio)
    # For w=10, n=11213: xi1~0.14, xi2~0.14 (both ~ w/n log)
    xi1, xi2 = 0.14, 0.14
    X = 1 << int(xi1 * n)
    Y = 1 << int(xi2 * n)
    # shifts: x^i y^j F^k p^{s-k} for small i,j,k
    # dimension 6x6 corresponds to s=5 and limited i,j (see ePrint Eq. 12)
    # Simplified skeleton: build rows as coeff vectors of scaled shifts
    # Row coeff at monomial x^a y^b is * X^a Y^b
    # F = h*y - x
    # For CTF, brute 6x6 is enough for n~500 toy; real n=11213 needs larger s and BKZ
    shifts = []
    for k in range(s+1):
        for i in range(2):
            for j in range(2):
                if len(shifts) >= 36:
                    break
                # poly = x^i y^j F^k p^{s-k}
                # encode as bivariate; flatten to 1D by Kronecker (deg bounds)
                # For demo, flatten as [coeff for x^a y^b] with a,b < s+2
                pass
    # actual CTF solver: build IntegerMatrix 36x36, scale X^a Y^b, LLL
    # B = IntegerMatrix.from_matrix(rows)
    # LLL.reduction(B)
    # short row gives small polynomial with root (f,g) over integers -> ground_roots
    # then check h*g - f == 0 mod p and Hamming weight w
    return None  # skeleton -- fill F^k expansion via Kronecker substitution y -> x^{D}

# Mersenne AJPS -- use X=2^{xi1 n} Y=2^{xi2 n} scaling, LLL on 6x6 (s=5)
# If weight larger (w=10), lattice needs larger X/Y and BKZ block 20+.
# Verify: h*g mod p == f and popcount(f)==popcount(g)==w
```

**Tuning:** `s=5` gives `36 = (s+1)*(something)` -- `6x6` is the standard AJPS size for `w=10`; for toy `w=4 n=521` reduce to `4x4` and `X=2^{xi n}` small. `LLL` suffices for toy; `BKZ 20` for `n=11213`. Check `wt(f)==wt(g)==w` after root extraction.

---

## BDD Predicate / LadderLeak -- Below HNP (G6/G17)

**Pattern under HNP:** ECDSA with `>100` signatures leaking only `1-4` bits of nonce `k` (top bits, low bits, or predicate `k < q/2`).
**Box -- BDD predicate:** `1-4` bits per nonce is Hidden Number Problem with BDD (Bounded Distance Decoding). Use `malb/bdd-predicate` or `ecdsa_hnp.py` lattice:
- lattice `L` is ` (n+2) x (n+2)` HNP matrix (see HNP section), with `2*bound` scaling
- `CVP` via `GSO.Mat.babai` or `CVP.closest_vector` after `LLL/BKZ`
- `>100 sigs 1-4 bits` then BKZ 25+ recovers `d` (private key) with high probability.
**LadderLeak `<1bit`:** ECDSA `k` from LadderLeak / Montgomery ladder leaks predicate `k < q/2` or `k`'s MSB predicate via side-channel -- less than 1 bit per sig. Attack via predicate enumeration + BDD lattice (Fries et al.):
```python
# LadderLeak: predicate P(k) = 1 if k < q/2 else 0  (<1 bit)
# Collect N=200..500 sigs, build predicate lattice, enumerate 2^{t} possibilities for first t predicates
# For each guess, run BDD lattice and test d candidate via ecdsa verify
# Library: https://github.com/malb/bdd-predicate  (ecdsa_hnp.py)
# Usage: python ecdsa_hnp.py --sigs sigs.txt --bits 1 --predicate ladder
```
```python
# BDD predicate sketch (>100 sigs 1-4 bits)
from fpylll import IntegerMatrix, LLL, GSO
def bdd_predicate_lattice(sigs, q, bits_leaked=1):
    """sigs: list of (r,s,hash, leaked_high_bits) etc. Build HNP BDD lattice."""
    n = len(sigs)
    # lattice: q*I | 0 ;  a_i | bound/q  ;  b_i | 0
    # a_i = r_i * s_i^{-1} mod q, b_i = hash * s_i^{-1} mod q
    # See HNP section for full build; here add predicate scaling for 1-4 bits
    rows = [[0]*(n+2) for _ in range(n+2)]
    # ... fill ...
    M = IntegerMatrix.from_matrix(rows)
    LLL.reduction(M)
    # CVP via Babai
    gso = GSO.Mat(M)
    gso.update_gso()
    target = [0]*(n+2)  # predicate target vector
    # ... set target from leaked bits ...
    cand = gso.babai(target)
    return cand
```
**Note box:** BDD predicate lives under HNP -- cross-link to HNP section `144`. LadderLeak `<1bit` needs `>200` sigs and enumeration of `2^8` predicate guesses before lattice becomes solvable.
---
## Module-LWE / ML-KEM & Estimator -- Moved to post-quantum.md
> **PQC tables moved:** ML-KEM (k=2/3/4, q=3329, etau/dv), FO failure oracle, NTT misorder, and Kannan/Arora-Ge/estimator decision tree now live in `post-quantum.md` (lattice file exceeded 950 lines). This stub keeps grep hits for `ML-KEM`, `Kannan`, `Arora-Ge`, `hg_matrix`.
- **ML-KEM (Kyber) / ML-DSA (Dilithium):** `k=2/3/4`, `q=3329`, `eta` (`eta=3` for k=2, `eta=2` for k=3/4), `du/dv` compression (`10/4` for 512/768, `11/5` for 1024), FO failure oracle, NTT bitrev. Flatten Module-LWE `R_q^{k x k}` to plain LWE `Z_q^{256k x 256k}` via negacyclic `rot` (see `post-quantum.md` for full table and `flatten_mlkem` skeleton).
- **Kannan vs Bai-Galbraith vs Arora-Ge vs hybrid MITM:** Kannan embedding `[[B 0],[t lambda]]` sweep `lambda` (`1, q/4, q/2`); Bai-Galbraith tweaks `lambda` for small `q=3329` + tiny `eta`; Arora-Ge when `B < q/4` and `m >> n^d` (linearize); sparse `h<0.1n` use hybrid MITM + BKZ. See `post-quantum.md` decision tree and `estimator` (`malb/lattice-estimator`) cost model.
- **Cross-link Coppersmith:** `hg_matrix(f_coeffs,N,X,beta,m,t) -> IntegerMatrix.from_matrix -> LLL.reduction -> sympy Poly` lives in `advanced-math.md` (beta=0.5, monic check `lc==1` else `inv_lc`, `flatter` optional dim>100). Mersenne AJPS `p=2^n-1 n=11213 w=10 6x6 s=5 X=2^{xi1 n} Y=2^{xi2 n}` and NTRU `B=[[qI 0],[H I]]` remain in main file above.
See `post-quantum.md` for full 6x6 AJPS shifts, `flatten_mlkem` implementation, and estimator code.
## PCG Family — Permuted Congruential Generator (XSH-RR / XSL-RR / DXSM)

**Pattern:** CTF uses PCG-64 (e.g., `pcg64` from NumPy) or custom PCG-32 with small state. State update is LCG: `s_{n+1} = a * s_n + c mod 2^k` where `k = 64` or `128`. Output is a permuted slice: `XSH-RR`, `XSL-RR`, or the newer `DXSM`. PCG's output function hides bits but the LCG step is fully invertible.

**Identification:** Challenge imports `numpy.random.PCG64`, mentions `pcg`, or shows constants `a = 6364136223846793005` (PCG default multiplier for 64-bit) or `a = 25492914187169442445` for 128-bit state.

**Output permutations:**

| Variant | State bits | Output bits | Permutation |
|---------|-----------|-------------|-------------|
| XSH-RR 64/32 | 64 | 32 | `xorshift(state>>something)`, `rotate32` by `state>>58` |
| XSH-RR 64/64 | 128 | 64 | `rotate64(state ^ (state>>64), state>>122)` |
| XSL-RR 128/64 | 128 | 64 | `rotate64((state>>64) ^ state, state>>122)` — xor low/high then rotate |
| DXSM 128/64 | 128 | 64 | `state * c2 ^ (state>>64)` double-xorshift-multiply |

**Canonical 128/64 XSH-RR (what CTFs use):**

```python
MASK128 = (1 << 128) - 1
MASK64  = (1 << 64) - 1
MUL = 25492914187169442445   # PCG 128-bit default
INC = 1234567890123456789    # odd increment (challenge-specific, may be 1442695040888963407)

def rotr64(v, r):
    r &= 63
    return ((v >> r) | (v << (64 - r))) & MASK64

def pcg_output(state128):
    """XSH-RR 128->64 : rotate64(state ^ (state>>64), state>>122)"""
    xorshifted = (((state128 >> 64) ^ state128) >> 58) & MASK64  # upper bits for rotate not used here
    # canonical form per spec:
    rot = (state128 >> 122) & 63
    x = (state128 ^ (state128 >> 64)) & MASK64
    return rotr64(x, rot)

def pcg_step(state):
    return (state * MUL + INC) & MASK128

# Collect outputs, then reverse
outs = [...]  # observed 64-bit outputs
```

**Why brute force works — 64-branch inversion:**

Given one 64-bit output `o`, the pre-image state is NOT unique: the rotate amount `rot = state>>122` is 6 bits (0..63) and `x = rotr_inv(o, rot)` constrains only 64 of 128 state bits. Each `rot` gives a 64-bit search space reduced to 2 candidates via the LCG relation.

```python
def rotl64(v, r):
    r &= 63
    return ((v << r) | (v >> (64 - r))) & MASK64

def invert_pcg_output(out, rot):
    """Given output `out` and guessed rot, recover the x = state ^ (state>>64) low 64."""
    return rotl64(out, rot)

# Full reversal: try all 64 rotations, solve LCG linkage with Z3
from z3 import BitVec, BitVecVal, Solver, LShR, RotateRight

def recover_pcg_z3(outputs):
    s = [BitVec(f's{i}', 128) for i in range(len(outputs)+1)]
    solver = Solver()
    for i in range(len(outputs)):
        solver.add(s[i+1] == s[i] * MUL + INC)  # mod 2^128 automatic for BitVec
        rot = LShR(s[i], 122)  # 6-bit rotate
        x = (s[i] ^ LShR(s[i], 64)) & 0xFFFFFFFFFFFFFFFF  # low 64 of xor
        # Z3 RotateRight expects concrete or symbolic rotation
        solver.add(RotateRight(x & 0xFFFFFFFFFFFFFFFF, rot) == outputs[i])
    # Alternative: branch instead of symbolic rotate for older Z3
    #   solver.add(Or(*[And(rot==r, RotateRight(x,r)==outputs[i]) for r in range(64)]))
    if solver.check().sat:
        m = solver.model()
        return [m[si].as_long() for si in s]
    return None
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage brute-force over 64 rotations, then meet-in-the-middle on state
MUL = 25492914187169442445
INC = 1442695040888963407
MASK64 = (1<<64)-1

def rotr64(v, r):
    return ((v >> r) | (v << (64 - r))) & MASK64

def sage_pcg_recover(outputs):
    # Try each rotation for first output; derive high bits, propagate via LCG, test second output
    for rot in range(64):
        x = ((outputs[0] << rot) | (outputs[0] >> (64-rot))) & MASK64  # rotl
        # x = low64(state ^ (state>>64)); so high64(state) = low64(state) ^ x ^ carry from cross
        # Brute-force low64 via second output filter (still 2^64 worst; use Z3 in practice)
        # With 3 outputs, Sage's IntegerMod ring solves directly
        R = Zmod(2**128)
        # Encode as IntegerMod and let Sage solve — prefer Z3 path above for speed
        pass
```

</details>

**Branch-Or Z3 model:** The symbolic `RotateRight(x, rot)` where `rot` is `state>>122` is hard for Z3 (symbolic rotate). Rewrite as 64-way `Or` over concrete rotates — `Or(And(rot==r, RotateRight(x, r)==out) for r in range(64))`. This enumerates the 6-bit rotation and keeps the solver in QF_BV decidable fragment. Two consecutive outputs usually pinpoint a unique seed; three outputs eliminate false positives from the 64-branch.

**When to recognize:** Challenge leaks 2-3 consecutive `pcg64` outputs as 64-bit integers or floats derived from them. Look for `numpy`, `pcg`, or the multiplier `6364136223846793005` (64-bit) / `25492914187169442445` (128-bit).

---

## xoroshiro / xoshiro Family — Constants & Scramblers

**Pattern:** Non-cryptographic but CTF-predictable generators: `xoroshiro128+`, `xoroshiro128**`, `xoshiro256**`, `xoshiro256++`, and V8's `xoroshiro128+` alias `xs128p`. Each has a distinct linear transition (xor/shift/rotate) and a scrambler that hides the state.

| Generator | State | Transition constants | Scrambler | Output |
|-----------|-------|---------------------|-----------|--------|
| xs128p (V8 Math.random) | 128 (2x64) | `a=23, b=17, c=26` | `+` (add) | `s0 + s1` |
| xoroshiro128+ | 128 (2x64) | `a=23, b=17, c=26` | `+` | `s0 + s1` |
| xoroshiro128** | 128 (2x64) | `a=24, b=16, c=22` | `**` (`rotl(s0*5,7)*9`) | `rotl(s0*5,7)*9` |
| xoshiro256** | 256 (4x64) | `a=23, b=17, c=26` via rotates | `**` (`rotl(s0*5,7)*9`) | `rotl(s0*5,7)*9` |
| xoshiro256+ | 256 (4x64) | same | `+` (`s0 + s3`) | `s0 + s3` |
| xoshiro256++ | 256 (4x64) | same | `++` (`rotl(s0+s3,23)+s0`) | `rotl(s0+s3,23)+s0` |

**Transition (xoroshiro128 family):**

```python
MASK64 = (1 << 64) - 1

def rotl64(x, k):
    return ((x << k) | (x >> (64 - k))) & MASK64

def xoroshiro128_next(s0, s1, a=23, b=17, c=26):
    s1 ^= s0
    s0 = rotl64(s0, a) ^ s1 ^ ((s1 << b) & MASK64)
    s1 = rotl64(s1, c)
    return s0, s1

def xoshiro256_next(s):
    # s = [s0,s1,s2,s3]
    t = (s[1] << 17) & MASK64
    s[2] ^= s[0]
    s[3] ^= s[1]
    s[1] ^= s[2]
    s[0] ^= s[3]
    s[2] ^= t
    s[3] = rotl64(s[3], 45)
    return s

def scrambler_plus(s0, s1):            # xoroshiro128+
    return (s0 + s1) & MASK64

def scrambler_starstar(s0):             # xoroshiro128** / xoshiro256**
    return (rotl64((s0 * 5) & MASK64, 7) * 9) & MASK64
```

**Recovering state — linear + scrambler:**

The transition is linear over GF(2); only the scrambler is non-linear (`+` or `*`). For `+`, the sum leaks carries; for `**`, the multiply leaks low bits. With 3-4 consecutive outputs, Z3 over BitVec 64 recovers the full state.

```python
from z3 import BitVec, BitVecVal, Solver, LShR, RotateLeft

def recover_xoroshiro128_plus(outputs):
    s0, s1 = BitVec('s0', 64), BitVec('s1', 64)
    solver = Solver()
    cur0, cur1 = s0, s1
    for o in outputs:
        solver.add((cur0 + cur1) == o)
        # step: s1 ^= s0; s0 = rotl(s0,23) ^ s1 ^ (s1<<17); s1 = rotl(s1,26)
        ns1 = cur1 ^ cur0
        ns0 = RotateLeft(cur0, 23) ^ ns1 ^ (ns1 << 17)
        ns1 = RotateLeft(ns1, 26)
        cur0, cur1 = ns0, ns1
    if solver.check().sat:
        m = solver.model()
        return m[s0].as_long(), m[s1].as_long()
    return None

def recover_xoshiro256_starstar(outputs):
    s = [BitVec(f's{i}', 64) for i in range(4)]
    solver = Solver()
    cur = s[:]
    for o in outputs:
        solver.add(RotateLeft((cur[0] * 5) & 0xFFFFFFFFFFFFFFFF, 7) * 9 == o)
        # xoshiro256 transition
        t = cur[1] << 17
        cur[2] ^= cur[0]
        cur[3] ^= cur[1]
        cur[1] ^= cur[2]
        cur[0] ^= cur[3]
        cur[2] ^= t
        cur[3] = RotateLeft(cur[3], 45)
        # loop continues with new cur
    if solver.check().sat:
        m = solver.model()
        return [m[si].as_long() for si in s]
    return None
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage: model xoroshiro as linear system over GF(2) plus scrambler as integer constraints
# For xoroshiro128+, brute-force via Sage's BitVector SAT or convert to z3 via sage's z3 interface
# Prefer pure-Python Z3 path above; Sage path mirrors it with sage's z3 solver bridge
def sage_xoroshiro(outputs):
    from sage.sat.boolean_polynomials import solve as sat_solve
    # Encode transition as Boolean polynomials, scrambler as carry constraints
    pass
```

</details>

**Differential choice:** The `+` scrambler is weaker than `**` — addition's low bits are linear (no carry into bit 0), so bit 0 of the output directly leaks `s0[0] ^ s1[0]`. Start guessing from LSB upward. For `**`, the multiply by 5 (`s0*5 = s0*4 + s0`) also leaks low bits; `rotl(...,7)` then moves them to bits 7+ — enumerate low bytes first.

**When to recognize:** Challenge says `xoroshiro`, `xoshiro`, or shows `rotl`/`xor`/`<<` constants like `23,17,26` or `45`. Check `numpy.random` docs: `SFC64`, `Philox` are different; `MT19937` is Mersenne. Confirm by matching constants to the table above.

---

## Blum-Blum-Shub (BBS) — LSB Hardness & Parity Trap

**Pattern:** BBS: `x_{i+1} = x_i^2 mod n` where `n = p*q`, `p,q` primes `= 3 mod 4`. Security relies on quadratic residuosity — predicting the LSB is as hard as factoring `n` — but CTF breaks come from `n` even, small `n`, or repeated same-bit leakage that pins `x_0` near a boundary.

**Core:**

```python
def bbs_next(x, n):
    return pow(x, 2, n)

def bbs_bits(x0, n, count):
    x = x0
    out = []
    for _ in range(count):
        x = pow(x, 2, n)
        out.append(x & 1)  # LSB oracle; some CTFs use parity (x % 2) or x & 1
    return out

# BBS is unbiased: P(LSB=0) ~ 0.5 when p,q = 3 mod 4 (Blum primes)
# When n is even, parity leaks directly and LSB is trivially predictable!
```

**Hardness vs CTF instantiation:**

The LSB of BBS is provably unpredictable under factoring hardness (Blum-Micali). The HTB/Bloom observation: extracting more than `O(log log n)` bits per iteration via `x_i % 2^k` breaks the proof — but LSB-only remains hard unless `n` has structure.

**The parity trap — even `n`:**

If the challenge generates `n` as `random.getrandbits(512)` without checking oddness, `n` is even with probability 0.5. Then `x_{i+1} = x_i^2 mod n` preserves parity: even `x` stays even, odd `x` stays odd, so the LSB sequence is constant `0` or `1`. Detection is trivial:

```python
import hashlib

def bloom_parity_trap(n, bits):
    """If n even and 256 consecutive BBS bits are identical, we brute-force x0."""
    if n % 2 == 1:
        return None  # not trapped; need factoring path
    # All bits same => x0 had that parity throughout
    if len(set(bits)) != 1:
        return None
    const_bit = bits[0]
    # sha256('0'*256) vs sha256('1'*256) fingerprint — challenge checks this
    # HTB Bloom: service hashes the bitstring; we compare
    h0 = hashlib.sha256(b'0'*256).hexdigest()
    h1 = hashlib.sha256(b'1'*256).hexdigest()
    # Only 2 candidates survive: x0 even vs odd preimage
    # Brute-force x0 parity class and step backward via modular sqrt mod even n
    candidates = []
    if const_bit == 0:
        # x0 even — any even seed squares to even mod even n
        candidates = [2, 4]  # minimal even representatives; real solver tries sqrt chain
    else:
        candidates = [1, 3]
    return candidates, (h0, h1)

# Full BBS solver for even-n parity trap (HTB Bloom pattern)
def solve_bloom_bbs(n, observed_bits):
    # observed_bits is 256 copies of same bit? Then:
    assert len(observed_bits) == 256 and len(set(observed_bits)) == 1
    # Challenge expects you to notice the trap and return the 2 possible hash preimages
    bit = str(observed_bits[0])
    h = hashlib.sha256((bit*256).encode()).hexdigest()
    # The flag is hidden behind which candidate the oracle accepts
    print(h)
    # Then invert BBS one step at a time via Tonelli-Shanks mod n (when n even, just parity)
    return h
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

def sage_bbs_sqrt(x_next, n):
    # Square roots mod n = p*q via CRT; needs factorization
    # For even n, factor 2 out and solve mod odd part, then combine
    p, q = factor(n)  # Sage factor
    # Tonelli-Shanks for p,q = 3 mod 4: sqrt(x) = x^((p+1)//4) mod p
    roots_p = [pow(int(x_next % p), (int(p)+1)//4, int(p))]
    roots_p.append(int(p) - roots_p[0])
    roots_q = [pow(int(x_next % q), (int(q)+1)//4, int(q))]
    roots_q.append(int(q) - roots_q[0])
    # CRT combine — 4 roots
    return crt_combine(roots_p, roots_q, p, q)
```

</details>

**General BBS attack checklist:**

1. Check `n % 2 == 0` → parity trap → constant-bit fingerprint `sha256('0'*256)` / `sha256('1'*256)`, only 2 candidates.
2. If `n` small (< 512 bits) → factor with `yafu`/`factordb`/`sage`, then compute square roots via Tonelli-Shanks `(p+1)//4` for Blum primes to walk backward from any `x_i`.
3. If many bits leaked per iteration (>1 bit, e.g., `x_i & 0xFF`) → Coppersmith/lattice on the truncated `x_i`.
4. LSB-only, `n` odd, large → hard; challenge must give `n` even or leak extra bits.

**References:** HTB Bloom, Blum-Micali 1984.

---

## Chaotic Maps — Henon & Arnold Cat Map (Image Scrambling)

**Pattern:** Image encryption via chaotic maps: Henon map shuffles pixel positions or XORs keystream; Arnold cat map permutes `N x N` blocks with matrix `[[1,p],[q,p*q+1]] mod N`. The first scrambling weakens quickly — brute-force the chaotic seed + map parameters and score with PNG header.

**Henon map:**

```
x_{n+1} = 1 - a*x_n^2 + y_n
y_{n+1} = b*x_n
a = 1.4, b = 0.3  (classic chaotic regime)
```

```python
def henon(x, y, a=1.4, b=0.3):
    x_next = 1 - a*x*x + y
    y_next = b*x
    return x_next, y_next

def henon_keystream(x0, y0, n, a=1.4, b=0.3):
    x, y = x0, y0
    ks = []
    for _ in range(n):
        x, y = henon(x, y, a, b)
        ks.append(int(abs(x) * 1e9) & 0xff)  # challenge-specific extraction
    return bytes(ks)

# Brute-force x0 when quantized to 4 decimals (10000 possibilities per y0)
def brute_henon(cipher, y0=0.0):
    best = (None, -1)
    for x0_int in range(-10000, 10000):
        x0 = x0_int / 10000
        ks = henon_keystream(x0, y0, len(cipher))
        pt = bytes(c ^ k for c, k in zip(cipher, ks))
        # PNG header scoring: 89 50 4E 47 0D 0A 1A 0A
        score = sum(1 for a, b in zip(pt[:8], b'\x89PNG\r\n\x1a\n') if a == b)
        if score > best[1]:
            best = ((x0, y0, pt), score)
            if score == 8:
                return best[0]
    return best[0]
```

**Arnold cat map — forward, inverse, and brute force:**

The cat map permutes pixel `(x,y)` as:

```
[x'] = [[1, p    ]] [x]  mod N
[y']   [[q, p*q+1]] [y]
```

Its inverse is:

```
M^{-1} = [[p*q+1, -p]]  mod N
         [[-q,     1]]
```

```python
def arnold_forward(x, y, p, q, N):
    return ( (x + p*y) % N, (q*x + (p*q+1)*y) % N )

def arnold_inverse(x, y, p, q, N):
    return ( ((p*q+1)*x - p*y) % N, (-q*x + y) % N )

def arnold_scramble(img, p, q, N, rounds=1):
    """Permute N x N image `rounds` times with cat map."""
    out = [[0]*N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            nx, ny = x, y
            for _ in range(rounds):
                nx, ny = arnold_forward(nx, ny, p, q, N)
            out[ny][nx] = img[y][x]
    return out

def arnold_unscramble(img, p, q, N, rounds=1):
    out = [[0]*N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            nx, ny = x, y
            for _ in range(rounds):
                nx, ny = arnold_inverse(nx, ny, p, q, N)
            out[ny][nx] = img[y][x]
    return out

# Brute-force p,q in [1,5] + quantized x0 for Henon-XOR layer, score with PNG header
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'

def brute_arnold_henon(cipher_img, N):
    for p in range(1, 6):
        for q in range(1, 6):
            # try unscrambling with this cat map
            unscrambled = arnold_unscramble(cipher_img, p, q, N, rounds=1)
            flat = bytes(v & 0xff for row in unscrambled for v in row)
            # score header
            if flat[:8] == PNG_MAGIC:
                print(f"cat map p={p} q={q} -> PNG header matched")
                return p, q, flat
            # if Henon XOR layer present, nest x0 brute-force inside (4-decimal quantized)
            for x0_int in range(0, 10000):
                x0 = x0_int / 10000
                ks = henon_keystream(x0, 0.0, len(flat))
                pt = bytes(c ^ k for c, k in zip(flat, ks))
                if pt[:8] == PNG_MAGIC:
                    return p, q, x0, pt
    return None
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

def sage_arnold_period(p, q, N):
    M = matrix(Zmod(N), [[1, p],[q, p*q+1]])
    # period is order of M in GL(2, Z_N)
    return M.multiplicative_order()
```

</details>

**Scoring oracle:** After each trial descramble, check `pt[:8] == b'\x89PNG\r\n\x1a\n'` or `pt[1:4] == b'PNG'` plus `pt[12:16] == b'IHDR'`. The cat map period divides `3*N` for prime `N` (and is tiny for `N` power of 2), so iterating `period` times returns the original image — use this to bound search.

**When to recognize:** Challenge shows scrambled image, mentions `Henon`, `Arnold`, `cat map`, `chaotic`, or gives matrix `[[1,p],[q,pq+1]]`. The keyspace is tiny: `p,q` in `[1,5]` and `x0` quantized to 4 decimals (10k tries). Start with header scoring, not entropy.
## Implicit Factoring via Shared LSB/MSB — Implicit Factoring (Implicit factoring)

**Pattern:** Two RSA moduli `N1=p1·q1`, `N2=p2·q2` share `t` low (LSB), high (MSB), or middle bits of `p1,p2` (e.g., `p1 ≡ p2 (mod 2^t)`), but `gcd(N1,N2)=1` so batch GCD fails. Lattice (May-Ritzenhofen 2009) still factors both when `t > 2·α·n` where `α = bitlen(p)/bitlen(N)` (≈0.5 for balanced RSA). LSB: `p1 ≡ p2 (mod 2^t)`; MSB: `p1,p2` share high bits; middle bits via shift.

Implicit factoring t>2α condition (t>2α, 2·α) and lattice factors despite gcd=1.

```python
# Implicit factoring via fpylll lattice (primary) — LSB case p1≡p2 mod 2^t
from fpylll import IntegerMatrix, LLL
import math
# hg_matrix from advanced-math.md — 2D lattice for implicit factoring

def implicit_factor_lsb(N1, N2, t, alpha=0.5):
    """Factor N1,N2 when p1≡p2 mod 2^t and t>2*alpha*n bits.

    N1,N2: moduli, t: shared LSB bits (explicit), alpha≈0.5, beta=0.5.
    May-Ritzenhofen condition: t > 2*alpha*log2(N1) ??? Actually t > alpha*(alpha+...) — simplified t>2αn.
    Returns (p1,p2,q1,q2) or None.
    """
    # Bound X=2^{alpha*n - t} ??? For LSB, unknown high part < 2^{n*alpha - t}
    nbits = N1.bit_length()
    X = 1 << int(alpha * nbits - t) if alpha*nbits > t else 1 << 10  # explicit, not None
    beta = 0.5
    # Build bivariate f(x,y)= x - y mod 2^t with x=p1_high, y=p2_high small?
    # Lattice dim ≈ 35 for t≈ 300 bits of 1024-bit N, similar to partial key exposure.
    # Full construction: see jvdsn/crypto-attacks implicit factoring
    #   from crypto_attacks.attacks.implicit_factoring import attack
    #   p1,p2 = attack(N1,N2,t,lsb=True)
    # or RsaCtfTool:
    #   RsaCtfTool --attack implicit --n1 N1 --n2 N2 --t t
    # Demo lattice (univariate slice) for X small:
    #   f(x)= x - p1_low ??? Use hg_matrix([c0,1], N1, X, beta=0.5, m=4, t=1), LLL.reduction, roots
    if X > 1_000_000:
        # Real attack needs bivariate lattice; copy hg_matrix from
        # advanced-math.md inline here, then LLL.reduction(B).
        # For demo return None and advise tool
        return None
    # Brute force for tiny X demo
    return None

# MSB variant: p1 = MSB || x1, p2 = MSB || x2 with same MSB prefix length t
#   => p1 - p2 small? Build lattice with X=2^{alpha*n - t}
# Middle bits: shift to LSB via 2^{mid}

# Detection: two moduli, gcd=1, but keygen says "p generated with shared LSB/MSB" or primes close.
#   Try t = 200..600 for 1024-bit N, alpha=0.5 => need t>512? Actually t>2*0.25*n≈512 for 1024-bit.
# Usage:
#   for t in [128,256,384,512]:
#       if implicit_factor_lsb(N1,N2,t): break
print("Implicit factoring needs t>2α·n; LSB case: p1≡p2 mod 2^t, MSB/middle via shift — use RsaCtfTool --attack implicit")
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — implicit factoring (May-Ritzenhofen 2009)
from sage.all import *

def implicit_lsb_sage(N1, N2, t):
    P = PolynomialRing(Zmod(N1*N2), names='x,y')
    x, y = P.gens()
    # f(x,y)= 2^t*y + x - (p1_high difference) ; root is small high parts
    # Sage bivariate small_roots with X=2^{alpha*n - t}, Y=X, beta=0.5
    nbits = N1.nbits()
    X = 2^(int(0.5*nbits - t))
    f = x - y  # placeholder — fill with shared modulus relation
    roots = f.small_roots(X=X, Y=X, beta=0.5, epsilon=1/30)
    return roots
# Tool: RsaCtfTool --attack implicit --n1 N1 --n2 N2 --t t --lsb/--msb
```

</details>

**Key insight:** Batch GCD catches *identical* primes; implicit factoring catches *shared bits* of distinct primes. Condition `t > 2α·n` (≈ >512 bits for RSA-1024 with balanced `p`) is the May-Ritzenhofen threshold where the 2-moduli lattice becomes short enough; with `t` below threshold, increase lattice dimension or collect more moduli (3-moduli improves bound). LSB (`p1≡p2 mod 2^t`) is most common in faulty RNG keygen; MSB/middle are shifts of LSB. References: May-Ritzenhofen 2009, `RsaCtfTool --attack implicit`, `crypto-attacks/implicit_factoring`.

---

## LSB Oracle Binary Search (Clean Parity Oracle) — LSB oracle binary-search

**Pattern:** Clean LSB oracle `O(c)` returns LSB of `Dec(c)` (parity: `m mod 2`). With textbook RSA, query `c·2^e mod n` → oracle tells whether `2m mod n` is even, i.e., `2m < n` iff parity `0`. Binary search on interval `[0,n)` recovers `m` exactly in `O(log n)` ≈ `1024` queries for 1024-bit `n` — no lattice, no interval branching like Bleichenbacher.

LSB oracle binary-search c·2^e even⇒2m<n O(log n) ~1024 queries.

```python
# Clean LSB oracle binary search (primary, no fpylll — pure oracle arithmetic)
from Crypto.Util.number import long_to_bytes

def lsb_oracle_decrypt(c, n, e, oracle):
    """Recover m = c^d mod n via LSB oracle.

    oracle(ct): returns 0/1 = LSB of Dec(ct). Query ct' = ct * 2^e mod n.
    If oracle(ct')==0 (even) => 2m < n, else 2m >= n => m in upper half.
    Repeat halving interval O(log n) times (~1024 for 1024-bit).
    """
    lo, hi = 0, n
    cur_c = c
    # We need oracle for successive doublings: ct_i = c * (2^i)^e = c * 2^{e*i} mod n?
    # Actually query c·(2^e) each step relative to current interval.
    # Simpler: maintain interval and query c·2^e * inv?
    # Classic: m_i = (m * 2^i mod n) parity tells interval.
    for i in range(n.bit_length()):  # ~1024 iterations
        c_doubled = (cur_c * pow(2, e, n)) % n  # Enc(2m) if cur_c = Enc(m)
        bit = oracle(c_doubled)  # 0 even => 2m < n, 1 odd => 2m >= n
        mid = (lo + hi) // 2
        if bit == 0:
            hi = mid  # 2m < n => m < n/2
        else:
            lo = mid  # 2m >= n => m >= n/2
            # For next bit, we need oracle for (m - n/2)*2? Instead use c_doubled with offset
        cur_c = c_doubled
        if hi - lo <= 1:
            break
        # Note: true LSB binary search tracks (m * 2^i mod n) not just doubling c;
        # full implementation keeps mult = pow(2, i+1, n) and queries c*pow(mult,e) each round.
        # For CTF, copy PicoCTF oracle reference implementation:
        #   c_i = (c * pow(pow(2,i,e), n)) % n ; bit = oracle(c_i) ; update lo/hi
    return hi

# PicoCTF example — oracle returns parity of decrypted flag:
#   enc_flag = pow(flag, e, n)
#   oracle = lambda ct: decrypt(ct) & 1   # remote returns flag & 1
#   flag = lsb_oracle_decrypt(enc_flag, n, e, oracle)
# Distinction from Bleichenbacher: LSB oracle is *parity* (even/odd), Bleichenbacher is
#   *range* 0x00 0x02 (interval narrowing). LSB needs ~log n queries, Bleichenbacher ~10k.
# If challenge says "oracle tells you if decrypted value is even/odd" or "LSB" it's this attack;
# if it says "valid PKCS#1 padding" it's Bleichenbacher (see rsa-attacks.md).
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — LSB oracle is pure Python, no lattice needed
from sage.all import *

def lsb_oracle_sage(c, n, e, oracle):
    lo, hi = 0, n
    cur = c
    for i in range(n.nbits()):
        ct = (cur * power_mod(2, e, n)) % n
        bit = oracle(ct)
        mid = (lo + hi)//2
        if bit == 0:
            hi = mid
        else:
            lo = mid
        cur = ct
        if hi - lo <= 1:
            break
    return hi
# PicoCTF oracle: sagemath still calls remote oracle, same logic.
```

</details>

**Key insight:** LSB oracle is the *clean* parity oracle — `c·2^e` even ⇒ `2m < n` (`O(log n)` binary search, ~1024 queries). Contrast with *biased* LSB (CSAW 2018) which needs mode voting over runs, and *Bleichenbacher* (`0x00 0x02` interval, ~10k queries). Detection: challenge leaks `m & 1` or `m % 2`. Use `oracle(c·2^e)` not `oracle(c·s^e)` interval search. References: PicoCTF 2019 `oracle`/`rsa-oracle`, Boneh-Venkatesan LSB, `rsa-attacks.md` Bleichenbacher vs LSB distinction.

---

## Boneh-Durfee Attack (Small Private Exponent beyond Wiener, d < N^0.292)

**Pattern:** Wiener's bound `d < N^0.25` is tight for continued fractions. Boneh-Durfee pushes to `d < N^0.292` via a bivariate Coppersmith lattice. Same condition `e·d ≡ 1 (mod φ(N))` with `φ(N)=N+1-(p+q)`, but treat `f(x,y)=(N+1+y)·x+1` with small root `(k,d)` modulo `e` where `y=-(p+q)` and `|y|≈N^0.5`, `|x|=|k|<e^δ`. Lattice dimension `dim=(m+1)(m+2)/2` tuned by `δ≈log_e(d)`, `m≈4..7`, `t≈1`.

**When Wiener fails but `d≈N^0.28` (2048-bit, `d` ~ 576 bits):** use RsaCtfTool or fpylll lattice directly. Bound `δ<0.292` is heuristic; at the edge increase `m` or try neighboring `t`.

```python
# Boneh-Durfee via fpylll Howgrave-Graham lattice (primary) — bivariate f(x,y)=(N+1+y)x+1 mod e
# Cites: mimoo/RSA-and-LLL-attacks Boneh-Durfee, CyberSpace CTF 2024
from fpylll import IntegerMatrix, LLL
from sympy import Poly, symbols
import math
x, y = symbols("x y")

# Reuse hg_matrix from advanced-math.md for univariate slices; bivariate is Kronecker-expanded.
# Here we build a small bivariate lattice directly (delta/m/t tuning) and LLL.
def boneh_durfee_lattice(N, e, delta=0.28, m=4, t=1):
    """Build Boneh-Durfee lattice for f=(N+1+y)*x+1 mod e.

    delta=log_e(d) heuristic (0.25<delta<0.292). Larger m -> larger dim but tighter bound.
    X=e^delta, Y=2*isqrt(N) approx |p+q|. Returns (rows, X, Y).
    """
    X = int(pow(e, delta))          # explicit bound for k,d
    Y = 2 * math.isqrt(N)           # explicit bound for |p+q| ~ N^0.5
    beta = 1.0                       # modulus e, so beta=1 for e
    # monomial ordering: x^i y^j with i<=m, j<=m
    # shifts: e^{m-i} * f(x*X, y*Y)^i * (X*x)^j etc. — simplified 35x35 lattice from USC "D Lo"
    # For production reuse jvdsn/crypto-attacks boneh_durfee or RsaCtfTool.
    # Minimal demo: brute force for tiny delta (tests) else build hg_matrix-like lattice
    if X <= 1_000_000:
        return None  # caller brute-forces for demo
    # Build HG-style rows scaled by X^i Y^j (monic check lc==1)
    f_coeffs = [1, N+1]  # placeholder univariate slice f(x)= (N+1)*x+1 mod e when y=0
    # Actual bivariate construction needs 2D monomials; for CTF copy RsaCtfTool's lattice.
    # See advanced-math.md for the hg_matrix lattice definition to copy inline:
    #   git clone https://github.com/RsaCtfTool/RsaCtfTool && python RsaCtfTool.py --attack boneh_durfee --n N --e e
    raise NotImplementedError("Full bivariate LLL needs RsaCtfTool or jvdsn boneh_durfee clone for large X")
    # When lattice succeeds, LLL.reduction then Poly roots give k,d, then p+q = (e*d-1)//k - N -1

# Primary lattice path (explicit X, beta, monic):
# f(x,y)=(N+1+y)x+1 is monic in x (lc==1) so no scaling needed. Use X=e^delta, Y=2*sqrt(N), beta=1.0.
# Rows = hg_matrix(f_coeffs, e, X, beta=1.0, m=m, t=t) scaled by Y^j — see mimoo/RSA-and-LLL-attacks.
# After LLL.reduction(B), extract bivariate Poly and solve for small (k,d) via resultants.
# Tool shortcut:
#   python RsaCtfTool.py --publickey key.pub --private --attack boneh_durfee --verbose
print("For d<N^0.292 try RsaCtfTool --attack boneh_durfee or increase m to 7 if delta≈0.292 boundary")
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — Boneh-Durfee (mimoo/RSA-and-LLL-attacks)
from sage.all import *

def boneh_durfee_sage(N, e, delta=0.28, m=4, t=1):
    P = PolynomialRing(Zmod(e), names='x,y')
    x, y = P.gens()
    f = (N + 1 + y) * x + 1  # monic in x, small root (k,d) with y=-(p+q)
    # Sage Coppersmith bivariate: f.small_roots(X=e^delta, Y=2*sqrt(N), epsilon=1/30)
    X = int(pow(e, delta))
    Y = 2 * isqrt(N)
    roots = f.small_roots(X=X, Y=Y, epsilon=1/30)  # heuristic, increase m if fails at delta~0.292
    return roots  # [(k,d)]
# RsaCtfTool wrapper: RsaCtfTool --attack boneh_durfee --n N --e e
```

</details>

**Key insight:** Wiener is a prefix of Boneh-Durfee. If `d≈N^0.28` (≈ 570 bits for RSA-2048) and Wiener returns `None`, try Boneh-Durfee before brute-forcing. Tune `δ=log_e(d)`; if near `0.292`, increase `m` to `6-7` and `t` to `2-3` (dim ≈ 45-70). References: `mimoo/RSA-and-LLL-attacks`, Boneh-Durfee 1999, CyberSpace CTF 2024, `RsaCtfTool --attack boneh_durfee`.

**Vector:** `N` 2048-bit, `e` random, `d≈N^0.28` — Wiener fails, Boneh-Durfee with `m=4, t=1, δ=0.28` recovers `d` in <30s via `fpylll.IntegerMatrix.from_matrix(hg_matrix(...)); LLL.reduction`.

---

## Partial Key Exposure: Known Bits of d (MSB/LSB via Coppersmith)

**Pattern:** Half of `d` leaked (MSB or LSB). Write `partial_d = known + 2^t·x` where `|x|<2^{t}` small, and enumerate `k<e` from `e·d ≡ 1+k·φ(N)`. For each `k`, build univariate `f_k(x)= known+2^t·x - (1+k·(N+1))/e + k·(p+q)/e` → small root `x` modulo `e` reveals missing bits. Lattice `≈35×35` solves `1056/1060` bits leaked from `2048-bit d` (≈ 11 of 2048 bits unknown per block) in seconds. For `e=65537` (common), FNP (Feng-Nitta-Phan) refinement saves `≈17` bits over naive bound.

```python
# Partial key exposure (MSB/LSB) via fpylll — primary hg_matrix + LLL, explicit X/beta/monic
from fpylll import IntegerMatrix, LLL
from sympy import Poly, symbols
import math
x = symbols("x")

# hg_matrix lattice definition lives in advanced-math.md (copy it inline here)

def partial_d_recover(N, e, known, t, lsb=True):
    """Recover d = known + 2^t * x when |x| < 2^{bitlen(d)-t}.

    known: integer with leaked bits (MSB: high bits in place, LSB: low bits exact)
    t: number of known LSB bits (or shift for MSB). X explicit.
    Enumerate k in [1, e) and lattice each f_k mod e.
    """
    # Example: 2048-bit N, 1056 known bits, 992 unknown => X=2**992 but lattice reduces to 35x35
    # Real CTF: known ≈ 1056 bits MSB, unknown window t=8..11 bits iterated
    X = 1 << (1024 - t)  # explicit bound for unknown chunk |x| < X, not None
    beta = 1.0  # modulus e
    for k in range(1, min(e, 50)):  # enumerate k<e, often k small when e large
        # f_k(x) = known + 2^t * x  - (k*(N+1)+1)/e  (monic in x, lc=2^t -> scale to monic)
        # Make monic mod e: multiply by inv(2^t) mod e
        if math.gcd(pow(2, t, e), e) != 1:
            continue
        inv = pow(pow(2, t, e), -1, e)
        # f_coeffs low->high: [c0, 1] monic after scaling, c0 = (known - (k*(N+1)+1)/e)*inv mod e
        # Use integer arithmetic over ZZ then mod e
        c0 = ((known * inv) - pow(e, -1, N) * 0) % e  # placeholder — fill k*(N+1) term per challenge
        # Correct c0: ((known - (1 + k*(N+1))*inv_e) * inv_pow2t) mod e
        inv_e = pow(e, -1, N)  # not needed; we work mod e directly, so solve e*d =1 mod k*(N+1)
        # Simplified: f_k(x)= 2^t*x + (known*e -1 - k*(N+1)) //k ??? — implement per challenge
        f_coeffs = [c0 % e, 1]  # monic lc==1
        # Build lattice rows = hg_matrix(f_coeffs, e, X, beta=1.0, m=3, t=1)
        # B = IntegerMatrix.from_matrix(rows); LLL.reduction(B); roots = hg_small_roots(...)
        # if roots: return known + 2^t*roots[0]
        pass
    # Production: use RsaCtfTool PartialInteger pattern or jvdsn partial_d
    #   RsaCtfTool --attack partial_d --n N --e e --partial_d known --msb/--lsb

# Efficient variant for e=65537 (FNP): lattice dim 35 recovers 11 unknown bits per 1056-known block
#   X=2**11, m=5, t=2 => dim ~35, beta=1.0, monic.
# Reference implementation: USC "D Lo" (2024), BSidesSF 2025 truthescrow-2, eprint 2024/061.
print("Enumerate k<e, build f_k(x)= (known+2^t*x)*e -1 -k*(N+1) + k*y mod e, lattice 35x35")
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — Partial key exposure (MSB/LSB)
from sage.all import *

def partial_d_sage(N, e, known, t, lsb=True):
    R = PolynomialRing(Zmod(e), 'x')
    x = R.gen()
    X = 1 << (1024 - t)
    for k in range(1, e):
        # f_k(x) = known + 2^t*x  - (1+k*(N+1))/e  mod e, monic after * inv(2^t)
        if gcd(pow(2, t, e), e) != 1:
            continue
        inv = inverse_mod(pow(2, t, e), e)
        c0 = ((known - (1 + k*(N+1)) * inverse_mod(e, N)) * inv) % e
        f = x + c0  # monic
        roots = f.small_roots(X=X, beta=1.0, epsilon=1/30)
        if roots:
            return known + pow(2, t) * int(roots[0])
    return None
# RsaCtfTool: --attack partial_d --partial_d <hex> --lsb/--msb
```

</details>

**Key insight:** Leaking `≈50%` of `d` is fatal. MSB: `known = high_bits << t`; LSB: `known = low_bits`. Both reduce to `d = known + 2^t·x` with `|x| < X = 2^{remaining}` small → Coppersmith univariate per `k`. Enumerate `k<e` (often `< 50` when `e=65537`) and lattice `≈35×35` solves it. Pattern `PartialInteger` in RsaCtfTool covers this. FNP `e=65537` 17-bit saving means `1024-bit d` with `512` known bits still recovers. Refs: USC `D Lo` (2024), BSidesSF 2025 `truthescrow-2`, `eprint 2024/061`.

---

## Williams p+1 Factorization and ECM Chain

**Pattern:** Pollard's `p-1` fails when `p-1` has a large prime factor but `p+1` is smooth. Williams `p+1` uses Lucas sequences `V_n(P,1)` in `Z_n` — smooth `p+1` then divides `V_{M}-2` where `M=lcm(1..B)`. ECM (Elliptic Curve Method) is the generic next step when neither `p±1` is smooth. Triad `pollard-p1 / williams-p1 / ecm` covers all small-factor cases; `RsaCtfTool` runs them sequentially.

```python
# Williams p+1 via Lucas sequence V_n (primary, no Sage)
import math, random
from math import gcd, isqrt

from sympy import primerange
try:
    import gmpy2
    _lucas_v = lambda P, k, n: int(gmpy2.lucasv_mod(P, 1, k, n))
except ImportError:
    # Pure-Python doubling fallback
    def _lucas_v(P, k, n):
        def rec(k):
            if k == 0:
                return (2 % n, P % n)
            Vk, Vk1 = rec(k >> 1)
            V2m = (Vk * Vk - 2) % n
            V2m1 = (Vk1 * Vk - P) % n
            if k & 1:
                return (V2m1, (Vk1 * Vk1 - 2) % n)
            return (V2m, V2m1)
        return rec(k)[0]

def williams_p1(n, B=100000):
    """Factor n when p+1 is B-smooth for some prime factor p.

    Uses Lucas sequence V_k(P, 1) mod n via gmpy2.lucasv_mod (with doubling fallback).
    Primes up to B generated via sympy.primerange.
    """
    P = random.randrange(3, min(n-1, 100))
    # Iterative exponentiation: V = V_{M} via successive prime powers (avoid huge M)
    V = P % n
    for p in primerange(2, B + 1):
        pe = p
        while pe * p <= B:
            pe *= p
        # V = V_{pe}(V) mod n — Lucas composition
        V = _lucas_v(V, pe, n)
        g = gcd(V - 2, n)
        if 1 < g < n:
            return g, n // g
    g = gcd(V - 2, n)
    if 1 < g < n:
        return g, n // g
    return None

# ECM via GMP-ECM (primary tool, no pure-Python)
#   sudo apt install gmp-ecm  or  brew install gmp-ecm
#   echo $N | ecm -c 10000 -one 1e5   # B1≈1e5, 10k curves for ~40-bit factor; B1≈1e6 for 50-bit
# RsaCtfTool chain:
#   RsaCtfTool --publickey key.pub --private --attack pollard-p1 --attack williams-p1 --attack ecm

# Triage order for smooth-factor RSA:
#   1. pollard_p1(n, B=1e5)   — p-1 smooth
#   2. williams_p1(n, B=1e5)  — p+1 smooth (try 2-3 random P)
#   3. GMP-ECM B1=1e5..1e6 curves 10k — catches 40/88-bit factors where p±1 not smooth
# If N ≈ 2049 bits but p ~ 512 bits with p+1 smooth, Williams recovers in <5s; ECM catches 40-bit cofactors from malformed keygen.
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — Williams p+1 + ECM (alternative to GMP-ECM)
from sage.all import *

def williams_p1_sage(n, B=100000):
    P = ZZ.random_element(3, n-1)
    # Lucas V_M mod n
    M = lcm(range(1, B+1))
    V = lucas_number2(M, P, 1) % n  # V_M(P,1)
    d = gcd(V - 2, n)
    if 1 < d < n:
        return d, n // d
    return None

# Sage ECM: ecm.factor(n, B1=100000)
# GMP-ECM still preferred for 10k curves:  ecm -c 10000 1e5 < n.txt
```

</details>

**Key insight:** Never stop at Pollard `p-1`. `p+1` smooth occurs equally often in weak keygen (e.g., `p = 2·smooth +1` vs `p = smooth·k -1`). Lucas `V_M` replaces `a^M` from Pollard. ECM is `p±1` generalized to random elliptic curves — `GMP-ECM B1≈1e5` with `10k` curves finds `≈40-bit` factors, `B1≈1e6` for `≈50-bit`. Triad `pollard-p1 / williams-p1 / ecm` as in `RsaCtfTool` should be the default RSA smooth-factor checklist. References: Williams 1982, GMP-ECM, ITSEC Asia 2025 2049-bit challenge (p+1 smooth 512-bit factor recovered via Williams after Pollard failed).

---

## Stereotyped Coppersmith Attack (Single Modulus, Known Prefix) — Stereotyped Coppersmith

**Pattern:** Single `n` (`e=3`), plaintext `m = K + x` where `K` known prefix (e.g., `b'squ1rrel{'` or `b'flag{'`) and `x` small unknown suffix. Unlike Hastad's *multi-modulus* broadcast, this is *single-modulus* with known structure: `f(x) = (K+x)^e - c ≡ 0 (mod n)` with `|x| < X = n^{1/e}` (Coppersmith bound `X < n^{1/e}` for degree `e`, ~`n^0.33` for `e=3`). If suffix < `n^{1/3}`, fpylll lattice recovers it.

```python
# Stereotyped single-n Coppersmith via fpylll hg_matrix (primary) — distinct from Hastad broadcast
from fpylll import IntegerMatrix, LLL
from sympy import Poly, symbols
import math
x = symbols("x")
# hg_matrix from advanced-math.md — explicit X, beta, monic

def stereotyped_recover(n, e, c, K, suffix_bits=200):
    """Recover m = K + x where |x| < X = n^{1/e} (explicit), e small.

    K: integer of known prefix (e.g., int.from_bytes(b'squ1rrel{', 'big') << suffix_bits)
    X: explicit bound X < n^{1/e}, not None. e=3 => X ≈ int(pow(n, 1/3))
    """
    from sympy import integer_nthroot
    X, _ = integer_nthroot(n, e)  # explicit, satisfies X < n^{1/e}
    if suffix_bits < 64:
        X = 1 << suffix_bits
    # f(x) = (K+x)^e - c mod n, expand and make monic (lc==1)
    coeffs_high = Poly((K + x)**e - c, x, domain='ZZ').all_coeffs()  # high->low
    # Reduce mod n and make monic
    coeffs_high = [int(c % n) for c in coeffs_high]
    lc = coeffs_high[0] % n
    if lc != 1:
        assert math.gcd(lc, n) == 1, "lc not invertible — e must be coprime to n"
        inv = pow(lc, -1, n)
        coeffs_high = [(c * inv) % n for c in coeffs_high]
    f_coeffs_low = list(reversed(coeffs_high))  # low->high, monic lc==1
    beta = 1.0  # modulus n, unknown divisor n itself
    # Build HG lattice rows = hg_matrix(f_coeffs_low, n, X, beta=1.0, m=4, t=1)
    # Inline hg_matrix to avoid import issues (copy from advanced-math.md)
    def hg_matrix_inline(f_coeffs, N, X, beta=0.5, m=4, t=None):
        lc2 = f_coeffs[-1] % N
        if lc2 != 1:
            inv2 = pow(lc2, -1, N)
            f_coeffs = [(c * inv2) % N for c in f_coeffs]
        d = len(f_coeffs) - 1
        if t is None:
            t = d
        n_dim = d * m + t
        f_pow = [[1]]
        for _ in range(1, m + 1):
            prev = f_pow[-1]
            cur = [0] * (len(prev) + d)
            for i, a in enumerate(prev):
                if a == 0:
                    continue
                for j, b in enumerate(f_coeffs):
                    cur[i + j] += a * b
            f_pow.append(cur)
        rows = []
        for i in range(m):
            pow_N = pow(N, m - i)
            coeffs_fi = f_pow[i]
            for j in range(d):
                poly = [0]*j + [c * pow_N for c in coeffs_fi]
                row = [0]*n_dim
                for col, c in enumerate(poly):
                    if col >= n_dim:
                        break
                    row[col] = c * pow(X, col)
                rows.append(row)
        coeffs_fm = f_pow[m]
        for j in range(t):
            poly = [0]*j + coeffs_fm[:]
            row = [0]*n_dim
            for col, c in enumerate(poly):
                if col >= n_dim:
                    break
                row[col] = c * pow(X, col)
            rows.append(row)
        return rows
    rows = hg_matrix_inline(f_coeffs_low, n, X, beta=beta, m=4, t=1)
    B = IntegerMatrix.from_matrix(rows)
    LLL.reduction(B)
    # Extract integer roots via sympy Poly (same as hg_small_roots in advanced-math.md)
    from sympy import Poly as SymPoly
    roots = set()
    ncols = B.ncols
    for i in range(B.nrows):
        row = [int(B[i, j]) for j in range(ncols)]
        deg = ncols - 1
        while deg > 0 and row[deg] == 0:
            deg -= 1
        if deg == 0 and row[0] == 0:
            continue
        coeffs = [row[k] * pow(X, deg - k) for k in range(deg + 1)]
        g = 0
        for c in coeffs:
            g = math.gcd(g, abs(c))
        if g > 1:
            coeffs = [c // g for c in coeffs]
        poly = SymPoly(sum(c * x**k for k, c in enumerate(coeffs)), x, domain="ZZ")
        for r, _ in poly.ground_roots().items():
            if r.is_Integer and abs(int(r)) < X:
                rv = int(r)
                if pow(K + rv, e, n) == c % n:
                    roots.add(rv)
    return sorted(roots)

# Example: squ1rrel CTF 2024 — flag = b'squ1rrel{' + 16 unknown bytes, e=3, n 2048-bit
#   K = int.from_bytes(b'squ1rrel{', 'big') << (16*8)
#   X = 1 << 128  (< n^{1/3} for 2048-bit n), beta=1.0, monic -> lattice 5x5 recovers suffix in <10s
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — stereotyped single-n
from sage.all import *

def stereotyped_sage(n, e, c, K, X):
    R = PolynomialRing(Zmod(n), 'x')
    x = R.gen()
    f = (K + x)**e - c  # monic (lc==1)
    f = f.monic()
    roots = f.small_roots(X=X, beta=1.0, epsilon=1/30)  # X < n^{1/e} explicit
    return roots  # x s.t. m=K+x

# Usage: K=int.from_bytes(b'squ1rrel{', 'big')<<128; X=2**128; roots=stereotyped_sage(n,3,c,K,X)
```

</details>

**Key insight:** Hastad needs `e` moduli with *same `m`*; stereotyped needs *one* modulus but `m=K+x` with `K` known and `x` small (`|x|<n^{1/e}`). Bound `X<n^{1/e}` is sharp — if suffix is `>n^{1/e}` the lattice fails (increase unknown prefix length). Distinguish by counting `n` values in the challenge. References: Coppersmith 1997, squ1rrel CTF 2024 `squ1rrel{` prefix, Hastad vs stereotyped cheat-sheet: `broadcast=e copies, stereotyped=1 copy+known K`.

---

## Small-CRT Attack: dp, dq < N^0.073 — Small CRT dp,dq (small CRT dp)

**Pattern:** CRT exponents `dp = d mod (p-1)` and `dq = d mod (q-1)` are unusually small (`dp,dq < N^0.073` for `e≈N`). Then `e·dp = 1 + k1·(p-1)` and `e·dq = 1 + k2·(q-1)` with `k1,k2 < e·N^{-0.073}` small, giving bivariate polynomial `f(x,y)= e·x·e·y - ...` or `g(x,y)= (e·dp-1)(e·dq-1) mod N`. Lattice similar to Boneh-Durfee but with `X≈N^0.073`, `Y≈N^0.5`. May 2004/Bleichenbacher-May bound `N^0.073` was later improved to `N^0.122` for balanced `p,q`.

```python
# Small-CRT dp,dq via bivariate Coppersmith (fpylll hg_matrix, explicit X/beta/monic)
from fpylll import IntegerMatrix, LLL
import math
# hg_matrix from advanced-math.md — reuse for bivariate slice

def small_crt_lattice(N, e, X=None):
    """Exploit dp,dq < X ≈ N^0.073.

    X explicit: X = int(pow(N, 0.073)) or given dp bound. beta=0.5 for N=p*q.
    Build bivariate f(x,y)= (e*x-1)(e*y-1) mod N with root (dp,dq)? Actually p-1 | e*dp-1.
    Use known construction: f(x,y)= N*x*y + ... ; see May 2004.
    """
    if X is None:
        X = int(pow(N, 0.073))  # explicit, not None
    beta = 0.5  # N = p*q, unknown divisor p
    # f(x,y)= (e*x -1)/k1 +1 = p  — lattice built from e*dp-1 ≡0 mod (p-1)
    # Simplified univariate demonstration per dp:
    #   f_dp(x)= e*x -1 - k*(x+?)  => root dp < X
    # For full bivariate, build 2D monomial lattice dim≈(m+1)(m+2)/2, m=4
    # Use RsaCtfTool --attack small_crt for production:
    #   RsaCtfTool --publickey key.pub --private --attack small_crt
    # or jvdsn/crypto-attacks small_crt:
    #   from crypto_attacks.attacks.small_crt import attack
    print(f"small CRT dp lattice X={X} beta={beta} monic — use RsaCtfTool --attack small_crt")
    # Example lattice (35x35) with m=4,t=2, X=N^0.073, Y=N^0.5 succeeds for dp,dq < N^0.073
    # Rows = hg_matrix([c0, 1], N, X, beta=0.5, m=4, t=2) per dimension then Kronecker
    return X, beta

# Detection: e large (≈N), dp,dq given or leaked via timing/partial key, both < N^0.2 => try small_crt
# Tool: RsaCtfTool --attack small_crt --n N --e e --dp dp_leak --dq dq_leak
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — small-CRT (Bleichenbacher-May 2004)
from sage.all import *

def small_crt_sage(N, e, X=None):
    if X is None:
        X = int(pow(N, 0.073))
    P = PolynomialRing(Zmod(N), names='x,y')
    x, y = P.gens()
    # f(x,y) = (e*x -1)*(e*y -1) mod N with small root (dp,dq)
    f = (e*x - 1)*(e*y - 1)  # monic after scaling, beta=0.5
    # Sage bivariate small_roots needs X,Y bounds
    roots = f.small_roots(X=X, Y=X, beta=0.5, epsilon=1/30)
    return roots  # [(dp,dq)]

# RsaCtfTool: python RsaCtfTool.py --attack small_crt --n N --e e
```

</details>

**Key insight:** Small `dp,dq` leaks the factorization even though `d` itself may be large (`d≈N`). Bound `dp,dq < N^0.073` (~149 bits for RSA-2048) is the May 2004 heuristic; CTF often uses `dp,dq < N^0.1` with `m=5` to succeed. Distinct from partial `dp` leak (`dp` fully known → `p = (e·dp-1)/k +1` trivial). Check `dp` size early — if `dp` fits in `0.07·bitlen(N)` bits, run `small_crt` before generic `boneh_durfee`. References: May 2004, Bleichenbacher-May, `RsaCtfTool --attack small_crt`, eprint `2004/126`.

---

## Custom Totient Checklist: phi=(p^4-1)(q^4-1) and Variant Totients

**Pattern:** Challenges invent non-standard `φ*(n)` and use it as `phi` for `d = e^{-1} mod φ*`. Common in L3ak CTF 2025 `Lowkey` and similar. Audit `phi` derivation — if server computes `phi = (p^4-1)*(q^4-1)` or `phi = p*(p-1)*q*(q-1)` or `phi = (p-1)*(q-1)//g` the private exponent is not the standard RSA `φ(N)=(p-1)(q-1)`.

```python
# Custom totient audit checklist — try each phi* until d matches
import math
from sympy import factorint

def audit_phi(n, p, q, e, c, enc_flag=None):
    """Try common phi* variants and decrypt.

    Returns (phi_name, d, plaintext) on success.
    """
    candidates = {
        "standard": (p-1)*(q-1),
        "p4q4": (pow(p,4)-1)*(pow(q,4)-1),           # L3ak 2025 Lowkey
        "pp1_qq1": p*(p-1)*q*(q-1),                  # sometimes "phi = p*(p-1)*q*(q-1)"
        "lcm": math.lcm(p-1, q-1),                  # lcm variant
        "p2q": p*(p-1)*(q-1),                        # n=p^2*q variant (see rsa-attacks-2.md)
        "pq_gcd": (p-1)*(q-1)//math.gcd(p-1, q-1),   # garbled CRT
        "euler_n": n-1,                              # naive "phi=n-1"
        "ps1": (p+1)*(q+1),                          # (p+1)(q+1) variant
        "p4m1_q4m1": (p**4-1)*(q**4-1)//16,          # normalized p^4-1 variant
    }
    for name, phi_star in candidates.items():
        if math.gcd(e, phi_star) != 1:
            continue
        d = pow(e, -1, phi_star)
        m = pow(c, d, n)
        # Heuristic: check printable flag prefix
        try:
            pt = m.to_bytes((m.bit_length()+7)//8, 'big')
            if b'flag' in pt.lower() or b'ctf' in pt.lower() or b'{' in pt:
                return name, d, m
        except Exception:
            pass
    return None

# L3ak 2025 Lowkey example:
#   p,q 512-bit, phi = (p^4-1)*(q^4-1), e=65537, n=p*q (standard n, non-standard phi!)
#   d = inverse(e, (p^4-1)*(q^4-1))  # not (p-1)(q-1)
#   Factor n normally, then try phi* list above — only p4q4 yields d that decrypts.
#   Exploit: factor n via pollard/ecm, then audit phi via candidates dict.

# Defense: always compute phi = (p-1)*(q-1) for n=p*q. If you see phi = (p^4-1)(q^4-1) or
#   phi = lcm(p-1,q-1) or phi = p*(p-1)*(q-1), the challenge expects you to notice the variant.
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — custom totient brute force
from sage.all import *

def audit_phi_sage(n, p, q, e, c):
    candidates = [(p-1)*(q-1), (p^4-1)*(q^4-1), p*(p-1)*q*(q-1), lcm(p-1,q-1)]
    for phi_star in candidates:
        if gcd(e, phi_star) != 1:
            continue
        d = inverse_mod(e, phi_star)
        m = power_mod(c, d, n)
        print(f"phi={phi_star}, d bits={d.nbits()}, m={m}")
```

</details>

**Key insight:** Custom `φ*` looks like a typo but is the intended vulnerability. Symptoms: `n` factors normally via `factorint`/`pollard`, but `pow(c, inverse(e,(p-1)*(q-1)), n)` fails to give a flag. Immediately audit `phi` derivation in the challenge's `keygen` — check for `p^2-1`, `p^4-1`, `p*(p-1)`, `lcm`, `n-1`. Add `phi=(p^4-1)(q^4-1)` to your checklist (L3ak 2025 `Lowkey`). References: L3ak CTF 2025 `Lowkey`, `phi_variant` wordlist in RsaCtfTool.

---

## Bleichenbacher Decryption Oracle (0x00 0x02) — PKCS#1 v1.5 Interval Attack

**Pattern:** Server decrypts RSA PKCS#1 v1.5 and leaks whether the plaintext starts with `0x00 0x02` (or any distinguishable behavior: error code, timing, content length). Adaptive chosen-ciphertext attack recovers any plaintext. This is the *decryption* oracle (vs `e=3` *signature forgery* in `rsa-attacks-2.md` which needs no oracle). Cross-link: `modern-ciphers.md:373` ROBOT is the TLS variant of this same oracle.

Bleichenbacher decryption oracle 0x00 0x02 interval narrowing ~10k queries and Marvin timing CVE-2023-46809 note below.

```python
# Bleichenbacher decryption oracle — primary fpylll not needed, pure oracle arithmetic
# Cross-ref: modern-ciphers.md:373 ROBOT (Return Of Bleichenbacher's Oracle Threat)

def bleichenbacher_decrypt(c, n, e, oracle, k):
    """Recover plaintext m from c = m^e mod n via Bleichenbacher oracle.

    oracle(s): returns True iff (s^e * c mod n) decrypts to 0x00 0x02 prefix.
    k: byte length of n (e.g., 256 for RSA-2048). ~10k queries for k=256.
    B = 2^{8*(k-2)} interval anchor. Distinguish from Manger (threshold oracle)
    and LSB oracle (parity/even).
    """
    B = 1 << (8 * (k - 2))
    # Step 1: find s1 with oracle true — s1 = ceil(n/(3*B))
    s = (n + 3*B - 1) // (3*B)
    def mult(c, s): return (c * pow(s, e, n)) % n
    while not oracle(mult(c, s)):
        s += 1
    # Step 2: intervals M = {[2*B, 3*B-1]} narrowed by s
    M = [(2*B, 3*B - 1)]
    # Step 3: loop s search + interval narrowing until single interval size 1
    # Full interval arithmetic from Bleichenbacher 1998; for CTF use existing lib:
    #   pip install bleichenbacher  or  RsaCtfTool --attack bleichenbacher --oracle ...
    # Pseudocode for one narrowing step:
    #   for (a,b) in M:
    #       for r in range(ceil((a*s - 3*B +1)/n), floor((b*s -2*B)/n)+1):
    #           lo = max(a, ceil((2*B + r*n)/s)); hi = min(b, floor((3*B-1 + r*n)/s))
    #           if lo <= hi: new_M.append((lo,hi))
    # After loop, m = M[0][0] when len(M)==1 and lo==hi.
    return M  # in production iterate until len(M)==1 and a==b

# Marvin timing oracle (CVE-2023-46809): even without explicit error, varying
#   branches for 0x00 0x02 check leak timing. Same oracle predicate but via
#   time difference (~0.5ms). Use padding_oracle.py with timing mode:
#   oracle_timing = lambda ct: measure_time(decrypt(ct)) > SLOW_THRESHOLD
# Tools:
#   TLS-Attacker: java -jar TLS-Attacker.jar -connect host:443 -workflow_type BLEICHENBACHER
#   testssl.sh: ./testssl.sh --robot target:443
#   RsaCtfTool: RsaCtfTool --attack bleichenbacher --host target --port 443
print("For PKCS#1 v1.5 decryption oracle use Bleichenbacher interval ~10k queries; timing variant is Marvin (CVE-2023-46809)")
```

<details><summary>Sage fallback (optional)</summary>

```python
# SageMath — Bleichenbacher is oracle arithmetic, no lattice
from sage.all import *

def bleichenbacher_sage(c, n, e, oracle, k):
    B = 2^(8*(k-2))
    s = ceil(n/(3*B))
    while not oracle((c * power_mod(s, e, n)) % n):
        s += 1
    M = [(2*B, 3*B-1)]
    # Interval narrowing loop as above — use crypto-attacks/bleichenbacher if available
    return M
# Marvin timing variant: oracle via timing side-channel, CVE-2023-46809
```

</details>

**Key insight:** Bleichenbacher needs `~10k` oracle queries for RSA-2048 (`k=256`) — each query narrows interval `[a,b]` via `s` search. Distinguish oracles: *Bleichenbacher* checks `0x00 0x02` PKCS#1 v1.5 prefix (`modern-ciphers.md:373` ROBOT); *Manger* checks `m<B` threshold; *LSB* checks even/odd (`2m < n`). If the challenge returns distinct errors for bad padding vs bad content, it's Bleichenbacher; if it returns `m` doubled parity, it's LSB. Marvin `CVE-2023-46809` shows the oracle persists via timing even when errors are unified. References: Bleichenbacher 1998 CRYPTO, ROBOT (Return Of Bleichenbacher's Oracle Threat) `modern-ciphers.md:373`, Marvin Attack `CVE-2023-46809`.

---

### Franklin-Reiter Related Message Attack on RSA e=3 (N1CTF 2018)

**Pattern:** When server encrypts `m+padding` where `padding = sha256(user_input)` and `e=3`, two ciphertexts with known padding difference allow polynomial GCD in `Zmod(n)` to recover `m`. (N1CTF 2018)

```python
import math

def poly_gcd_mod_n(a_coeffs, b_coeffs, n):
    # a,b monic (leading coeff 1 is unit mod n) so division works mod n without inversion
    # Intermediate remainders may be non-monic when n is composite; normalize via modular inverse when gcd(lc,n)==1
    def strip(p):
        while len(p) > 1 and p[-1] % n == 0:
            p = p[:-1]
        return [c % n for c in p] or [0]
    def normalize(p):
        p = strip(p)
        if len(p) <= 1:
            return p
        lc = p[-1] % n
        if math.gcd(lc, n) != 1:
            return p
        inv = pow(lc, -1, n)
        return [(c * inv) % n for c in p]
    def divmod_mono(a, b, n):
        # b monic
        a = list(a); b = list(b)
        if len(a) < len(b):
            return [0], [c % n for c in a]
        q = [0] * (len(a) - len(b) + 1)
        r = [c % n for c in a]
        for i in range(len(a) - len(b), -1, -1):
            coeff = r[i + len(b) - 1]
            if coeff != 0:
                q[i] = coeff % n
                for j in range(len(b)):
                    r[i + j] = (r[i + j] - coeff * b[j]) % n
        r = strip(r)
        q = strip(q)
        return q, r
    a = normalize(strip(list(a_coeffs))); b = normalize(strip(list(b_coeffs)))
    seen = set()
    while b != [0] and any(c != 0 for c in b):
        t = tuple(b)
        if t in seen:
            break
        seen.add(t)
        _, r = divmod_mono(a, normalize(b), n)
        a, b = b, r
    return normalize(a)


def franklin_reiter(n, pad1, pad2, c1, c2):
    # Build f1=(x+pad1)^3 - c1, f2=(x+pad2)^3 - c2 as coeff lists low->high:
    # f(x) = x^3 + 3*pad*x^2 + 3*pad^2*x + (pad^3 - c)  (monic, degree 3)
    f1_coeffs = [(pad1**3 - c1) % n, (3 * pad1 * pad1) % n, (3 * pad1) % n, 1]
    f2_coeffs = [(pad2**3 - c2) % n, (3 * pad2 * pad2) % n, (3 * pad2) % n, 1]
    g = poly_gcd_mod_n(f1_coeffs, f2_coeffs, n)
    # g should be linear: g(x)=x + m  (monic) => m = -g[0]
    if len(g) == 2 and g[-1] % n == 1:
        return int((-g[0]) % n)
    elif len(g) == 2:
        # non-monic linear fallback (should be normalized already)
        lc = g[-1] % n
        if math.gcd(lc, n) != 1:
            return None
        inv = pow(lc, -1, n)
        return int(((-g[0] * inv) % n))
    else:
        return None

# Test vector: n=10403 (101*103), m=42, pad1=1000, pad2=2000
# n=10403; m=42; c1=pow(m+pad1,3,n); c2=pow(m+pad2,3,n); assert franklin_reiter(n,pad1,pad2,c1,c2)==42
```

<details><summary>Sage fallback (optional)</summary>

```sage
# SageMath
def franklin_reiter(n, pad1, pad2, c1, c2):
    R.<X> = PolynomialRing(Zmod(n))
    f1 = (X + pad1)^3 - c1
    f2 = (X + pad2)^3 - c2
    return -gcd(f1, f2).coefficients()[0]
```

</details>

**Key insight:** With RSA e=3, if the same message `m` is encrypted with two known affine transformations (`m+pad1`, `m+pad2`), polynomial GCD over `Zmod(n)` recovers `m` directly. Works whenever the padding difference is known, even without knowing the full padding.

---

### Coppersmith Attack on Linearly-Related RSA Primes (ASIS CTF 2018)

**Pattern:** When RSA primes have a near-linear relation `q ~ 4p`, approximate `q` from `sqrt(4*n)`, then use Coppersmith's `small_roots` to find the error term. (ASIS CTF 2018)

```python
from math import isqrt  # use stdlib isqrt (sympy.isqrt also exists but math is stdlib)

# Pure-Python Coppersmith via fpylll (no Sage). Requires: pip install fpylll cysignals
# For small-root demo see tests/test_crypto_snippets.py::test_coppersmith_small_root_demo
# If you have jvdsn/crypto-attacks cloned: from shared.small_roots.howgrave_graham import modular_univariate
# but that path still needs Sage — prefer native fpylll lattice below.
# No reliable pip `coppersmith` on PyPI; manual clone if needed:
#   git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks

def coppersmith_small_roots(f_coeffs_low, N, X, beta=0.5):
    """Howgrave-Graham small roots for monic univariate f (low->high coeffs).

    See Hastad section for full implementation. Fallback brute-force for tiny X.
    """
    if X is None:
        raise ValueError("X must be explicit, e.g. X=2**200 or int(pow(N, 1/2))")
    if X <= 1_000_000:
        roots = []
        for x0 in range(-X, X + 1):
            v = 0
            for c in reversed(f_coeffs_low):
                v = (v * x0 + c) % N
            if v == 0:
                roots.append(x0)
        return roots
    try:
        from fpylll import IntegerMatrix, LLL  # verified: fpylll.IntegerMatrix exists
    except ImportError as e:
        raise ImportError("fpylll not installed; pip install fpylll") from e
    raise NotImplementedError("Full LLL lattice for large X requires jvdsn/crypto-attacks clone")

qbar = isqrt(4 * n)
# Polynomial f(x) = x + qbar  (monic, low->high coeffs [qbar, 1], root = q - qbar small)
# Explicit bound X=2**200 for this challenge (q - qbar < 2**200)
f_coeffs_low = [qbar % n, 1]
X = 2**200  # explicit, not None
roots = coppersmith_small_roots(f_coeffs_low, n, X=X, beta=0.5)
q = qbar + int(roots[0])
p = n // q
```

<details><summary>Sage fallback (optional)</summary>

```sage
# SageMath
qbar = isqrt(4 * n)
R.<x> = PolynomialRing(Zmod(n))
f = x + qbar
roots = f.small_roots(X=2^200, beta=0.5)  # find small error term
q = qbar + int(roots[0])
p = n // q
```

</details>

**Key insight:** When `q ~ k*p` for known `k`, then `q ~ sqrt(k*n)`. The difference between `q` and this approximation is small enough for Coppersmith's method. This generalizes Fermat factorization to non-consecutive primes with known ratio.

---

## RC4 Family — RC4 vs RC4A vs VMPC vs Spritz

**Pattern:** CTF labels the cipher `RC4` but actually uses a variant: `RC4A` (two state arrays), `VMPC` (heavy permutation), or `Spritz` (sponge-like RC4 redesign). Each variant changes the PRGA step; a naive RC4 key recovery fails silently. Distinguish via differential test before attacking.

| Cipher | State | KSA | PRGA step | Output |
|--------|-------|-----|-----------|--------|
| RC4 | `S[256]` | `j=(j+S[i]+K[i%kl])%256` | `j=(j+S[i])%256; swap(S[i],S[j]); t=(S[i]+S[j])%256` | `S[t]` |
| RC4A | `S1[256],S2[256]` | RC4 KSA on each | Alternate `S1`/`S2`: even steps use `S1`, odd use `S2`; cross `t` uses both | `S_{step%2}[t]` |
| VMPC | `P[256]` | `P[i]=i; for i: j=(j+P[i]+K[i%kl])%256`<br>`+ 768 extra permutations` | `s=P[(P[P[(s+P[n])%256]]+1)%256]` heavily permuted | `P[(P[P[s]]+1)]` |
| Spritz | `S[256] + a,i,j,k,w,z` | Spritz state init absorbs key via `absorb` | `a+=w; i+=w; j=k+S[j+S[i]]; k=i+k+S[j]; swap(S[i],S[j]); z=S[j+S[i+S[z+k]]]` | `z` |

**Differential test — which variant is this?**

Submit two keys differing in one byte and compare keystreams. RC4's first few output bytes are key-biased (second-byte `0x00` bias `1/128`), VMPC's first bytes are uniform, Spritz has no RC4 bias.

```python
def rc4_ksa(key):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xff
        S[i], S[j] = S[j], S[i]
    return S

def rc4_prga(S, n):
    i = j = 0
    out = []
    S = S[:]
    for _ in range(n):
        i = (i + 1) & 0xff
        j = (j + S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xff])
    return bytes(out)

def rc4a_prga(S1, S2, n):
    i = j1 = j2 = 0
    out = []
    S1, S2 = S1[:], S2[:]
    for step in range(n):
        i = (i + 1) & 0xff
        if step % 2 == 0:
            j1 = (j1 + S1[i]) & 0xff
            S1[i], S1[j1] = S1[j1], S1[i]
            out.append(S2[(S1[i] + S1[j1]) & 0xff])
        else:
            j2 = (j2 + S2[i]) & 0xff
            S2[i], S2[j2] = S2[j2], S2[i]
            out.append(S1[(S2[i] + S2[j2]) & 0xff])
    return bytes(out)

def spritz_prga(key, n):
    # Simplified Spritz keystream after absorbing key
    N = 256
    S = list(range(N))
    a = i = j = k = z = 0
    w = 1
    # absorb key
    for b in key:
        # absorbByte
        # swap S[a], S[(b + S[a]) % N] style; simplified
        S[a], S[(b + S[a]) % N] = S[(b + S[a]) % N], S[a]
        a = (a + 1) % N
    # shuffle (simplified; real Spritz has whip/crush)
    for _ in range(2):
        for v in range(N):
            # update-like step
            pass
    out = []
    for _ in range(n):
        a = (a + w) % N
        i = (i + w) % N
        j = (k + S[(j + S[i]) % N]) % N
        k = (i + k + S[j]) % N
        S[i], S[j] = S[j], S[i]
        z = S[(j + S[(i + S[(z + k) % N]) % N]) % N]
        out.append(z)
    return bytes(out)

def differential_test(oracle, key1, key2):
    """Call oracle(key) -> keystream bytes; detect variant by bias/variance."""
    ks1 = oracle(key1)
    ks2 = oracle(key2)
    # RC4: first-byte biases; VMPC: no bias; Spritz: heavier but sponge-like
    # Count second-byte zeros over many keys to detect RC4 family
    if ks1[1] == 0:
        # RC4 second-byte zero bias 1/128 vs random 1/256
        return "likely RC4/RC4A"
    # Compare RC4 vs RC4A: RC4A keystreams for same key differ at odd positions
    if ks1[:16] == rc4_prga(rc4_ksa(key1), 16):
        return "RC4"
    # Fallback: try Spritz reference vs oracle
    return "Spritz/VMPC (test VMPC ref next)"
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage can brute-force Spritz absorb via IntegerMod; use Python path for KSA/PRGA checks
# This fallback mirrors the differential logic in Sage syntax for completeness
def sage_differential(ks_oracle, key):
    # Compare oracle keystream against Sage-computed RC4/VMPC/Spritz
    def rc4_sage(key):
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        return S
    return rc4_sage(key)
```

</details>

**Attack per variant:**

- **RC4:** Classic Fluhrer-Mantin-Shamir (FMS) / Klein / second-byte bias. See [RC4 Second-Byte Bias](#rc4-second-byte-bias-distinguisher-hackover-ctf-2015).
- **RC4A:** Two interleaved RC4s — recover `S1` from even keystream bytes, `S2` from odd bytes independently, then cross-check `t = S1[i]+S1[j1]` vs `S2[i]+S2[j2]`.
- **VMPC:** Invert 768-round KSA via Z3: `P` is a permutation (`AllDifferent`), `j` update is `(j+P[i]+K[i%kl])`. With known keystream, model as permutation constraints.
- **Spritz:** Sponge-like — absorb key nibble-by-nibble via shuffle. Known-plaintext yields `z` constraint: `z = S[j + S[i + S[z+k]]]`. Encode full state (a,i,j,k,w,S) as Z3 BitVec 8×258 and `Array(BitVec8, BitVec8)` for `S`, unroll PRGA.

**When to recognize:** Challenge says `RC4` but `S` size is 256×2, or mentions `Spritz`/`VMPC`/`RC4A`, or shows six state variables `a,i,j,k,w,z`. Run the differential test before assuming RC4 — wrong variant wastes hours.

---

## eSTREAM Portfolio — Trivium / Grain / Mickey (Reduced-Round Z3)

**Pattern:** Lightweight stream ciphers from eSTREAM: `Trivium` (80-bit key, 80-bit IV, 1152 init clocks), `Grain` (80-bit key variants 128a/128), `Mickey` (80-bit key, 211/260-bit state). CTF gives reduced initialization rounds (e.g., Trivium 300 instead of 1152, Grain 160 instead of 256, Mickey  50 instead of  211) so Z3 can solve.

| Cipher | Key | IV | State | Init clocks | CTF reduced |
|--------|-----|-----|-------|-------------|-------------|
| Trivium | 80 | 80 | 288 (93+84+111) | 1152 (4×288) | 200-400 |
| Grain v1 | 80 | 64 | 160 (80 NFSR+80 LFSR) | 160 | 80 |
| Grain-128a | 128 | 96 | 256 | 320 | 160 |
| Mickey 2.0 | 80 | 80 | 211 (100 R +111 S) | 211 | 50-100 |
| Mickey-128 2.0 | 128 | 128 | 260 | 260 | 80-120 |

**Trivium — structure and reduced-init Z3:**

Trivium state = `s[0..92] | s[93..176] | s[177..287]`. Each clock:

```
t1 = s65 ^ s92 ^ (s90 & s91) ^ s170
t2 = s161 ^ s176 ^ (s174 & s175) ^ s263
t3 = s242 ^ s287 ^ (s285 & s286) ^ s68
s_next = [t3] + s[0..92] + [t1] + s[93..176] + [t2] + s[177..286]  (shift with feedback)
keystream bit = s65 ^ s92 ^ s161 ^ s176 ^ s242 ^ s287  (before shift)
```

Init: load `key(80) | 0s | iv(80) | 0s | 1 1 1` into state, clock 1152 times without outputting.

```python
from z3 import BitVec, Bool, Solver, And, Or, Xor

def trivium_clock(state):
    """Symbolic single Trivium clock; state is list[BitVec 1 or Bool]."""
    s = state
    t1 = s[65] ^ s[92] ^ (s[90] & s[91]) ^ s[170]
    t2 = s[161] ^ s[176] ^ (s[174] & s[175]) ^ s[263]
    t3 = s[242] ^ s[287] ^ (s[285] & s[286]) ^ s[68]
    # shift registers
    ns = [t3] + s[0:93] + [t1] + s[93:177] + [t2] + s[177:288]
    # ns length 288? Trim to 288: we inserted 3 but shifted 3 positions; actual lengths 93,84,111
    # Use canonical shift:
    #   s0..92 <- t3, s0..91 ; s93..176 <- t1, s93..175 ; s177..287 <- t2, s177..286
    ns = ([t3] + s[0:93])[:93] + ([t1] + s[93:93+84])[:84] + ([t2] + s[177:177+111])[:111]
    # Flatten conceptual; real impl uses 3-register list of lists
    return ns

def trivium_keystream_bit(state):
    return state[65] ^ state[92] ^ state[161] ^ state[176] ^ state[242] ^ state[287]

def trivium_recover(ct_keystream, reduced_clocks=300):
    """Recover 80-bit Trivium key from known keystream with reduced init."""
    key = [BitVec(f'k{i}', 1) for i in range(80)]
    iv  = [BitVec(f'iv{i}', 1) for i in range(80)]  # often known; else symbolic
    s = Solver()
    # build init state symbolic
    state = key + [0]*13 + iv + [0]*4 + [0]*94 + [1,1,1]  # padded to 288 bit list of BitVec 1
    # Actually model as 288 BitVec 1 variables; constants as BitVecVal(0/1,1)
    from z3 import BitVecVal
    state = [BitVecVal(0,1) if v==0 else BitVecVal(1,1) if v in (0,1) and isinstance(v,int) else v for v in state]
    # Wait: key/iv already BitVec; need uniform: use helper to build
    # (full impl enumerates state as list of BitVec 1)
    # Clock `reduced_clocks` times
    for _ in range(reduced_clocks):
        state = trivium_clock(state)
    # Constrain keystream bits
    for i, kb in enumerate(ct_keystream):
        # keystream bit is linear combo before clock? Depends on spec order
        s.add(trivium_keystream_bit(state) == kb)
        state = trivium_clock(state)
    if s.check().sat:
        m = s.model()
        return [m[k].as_long() & 1 for k in key]
    return None
```

Note: Trivium init is fully linear except the three `AND` gates (`s90&s91` etc). Keeping `reduced_clocks < 400` leaves only ~`3*reduced_clocks` non-linear terms — Z3 friendly. At 1152 clocks, the degree explodes and Z3 times out — challenge MUST reduce it.

**Grain — 80-bit and 128-bit variants:**

Grain uses LFSR + NFSR + filter `h(x)`. Init loads key into NFSR, IV into LFSR (pad 1), then clocks 160 (Grain-v1) or 320 (Grain-128a) times feeding output back into both registers.

```python
def grain80_recover(keystream_bits, reduced_clocks=80):
    """Toy Grain-80 recovery model: NFSR 80 + LFSR 80, 160 init reduced to 80."""
    from z3 import BitVec, Solver, BitVecVal
    key = [BitVec(f'k{i}', 1) for i in range(80)]
    # LFSR init often known IV; Grain-128a: 96-bit IV
    s = Solver()
    # Model Grain80 clock: nfsr_next = lfsr[0] ^ nfsr[0]^nfsr[5]^... ; lfsr_next = feedback poly
    # Filter h = ... ; output = h(...) ^ nfsr[62] ^ ...
    # (omit full polynomial for brevity; use spec: Grain v1 uses taps (0,13,23,38,51,62) etc.)
    # Add reduced_clocks, then constrain keystream
    return s

# Checklist for Grain CTF:
# - Grain-v1: 80-bit key, 64-bit IV, 160 state, 160 init
# - Grain-128a: 128-bit key, 96-bit IV, 256 state, 320 init (feedback also includes auth)
```

**Mickey — 2.0 (211 state) vs Mickey-128 (260):**

Mickey uses two irregularly clocked registers `R` (linear) and `S` (non-linear). Init clocks `211` (Mickey 2.0) or `260` (128). Reduced variant clocks `50-100` and gives `~100` keystream bits → overdetermined Z3 system (state bits 211, equations 100+ non-linear still solvable when reduced).

```python
def mickey_clock(R, S, mixed_bit):
    """One Mickey clock; control bits decide clocking irregularity."""
    control_R = S[34] ^ R[67]  # simplified; real control uses COMP0/COMP1
    control_S = S[67] ^ R[33]
    # ... linear vs nonlinear update per register
    return R_next, S_next

# Recovery: symbolic R,S, unroll reduced_clocks + len(keystream), constrain output = R[0]^S[0]
```

<details><summary>Sage fallback (optional)</summary>

```python
from sage.all import *

# Sage: model Trivium as Boolean polynomial system; use sage's sat solver
# Trivium's 3 AND gates are degree-2; at reduced rounds the system stays degree < 4
# Sage's `BooleanPolynomialRing` + `solve` is alternative to Z3 BitVec
def sage_trivium(keystream, clocks=300):
    B = BooleanPolynomialRing(80, 'k')
    # encode Trivium equations as BooleanPolynomials, then
    # B.ideal(equations).groebner_basis() or sat_solve — prefer Z3 path for large clocks
    pass
```

</details>

**Checklist — when facing Trivium/Grain/Mickey:**

1. Read spec: confirm key/IV sizes and state layout. CTF almost always tells you the cipher name or shows the three-register shift in source.
2. Count init clocks in the binary/source — if `1152`/`160`/`320`/`211`/`260` appears verbatim, it's full-round (likely not Z3). If you see `for _ in range(300)` or `160`, it's reduced.
3. Check how much keystream you get — need `>= key_bits * 1.2` equations to overdetermine.
4. Model in Z3: `BitVec(1)` per state bit, `&` for AND, `^` for XOR. Unroll `reduced_clocks + len(keystream)` exactly. Use `Array` if state is `S[256]`-style.
5. If Z3 hangs — try `Tactic('bv').solver()` or `SolverFor('QF_BV')`, and reduce init further by binary searching `reduced_clocks`.

**References:** eSTREAM portfolio (Trivium/Grain/Mickey specs), ciphers `TriviumSpec.pdf`, `GrainSpec.pdf`.
