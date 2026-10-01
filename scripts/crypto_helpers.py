#!/usr/bin/env python3
"""Small exact arithmetic helpers; offline only, with explicit limits and verification."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path


def integer_root(value: int, degree: int) -> tuple[int, bool]:
    if value < 0 or degree < 1:
        raise ValueError('nonnegative value and positive degree required')
    low, high = 0, 1 << ((value.bit_length() + degree - 1)//degree)
    while low < high:
        middle = (low + high + 1)//2
        if pow(middle, degree) <= value:
            low = middle
        else:
            high = middle - 1
    return low, pow(low, degree) == value


def crt(residues: list[int], moduli: list[int]) -> tuple[int, int]:
    if not residues or len(residues) != len(moduli) or any(n <= 0 for n in moduli):
        raise ValueError('equal nonempty arrays and positive moduli required')
    x, modulus = 0, 1
    for residue, other in zip(residues, moduli):
        divisor = math.gcd(modulus, other)
        if (residue-x) % divisor:
            raise ValueError('incompatible non-coprime congruences')
        reduced = other//divisor
        step = ((residue-x)//divisor * pow(modulus//divisor, -1, reduced)) % reduced if reduced != 1 else 0
        x += modulus*step
        modulus *= reduced
        x %= modulus
    return x, modulus


def egcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    while r:
        q = old_r//r
        old_r, r = r, old_r-q*r
        old_s, s = s, old_s-q*s
        old_t, t = t, old_t-q*t
    return old_r, old_s, old_t


def common_modulus(n: int, e1: int, e2: int, c1: int, c2: int) -> int:
    if n <= 1 or e1 <= 0 or e2 <= 0:
        raise ValueError('invalid RSA parameters')
    divisor, a, b = egcd(e1, e2)
    if divisor != 1:
        raise ValueError('exponents must be coprime; otherwise only a power of the message is recovered')
    try:
        message = (pow(c1, a, n)*pow(c2, b, n)) % n
    except ValueError as error:
        raise ValueError('ciphertext is not invertible; gcd(ciphertext,n) may reveal a factor') from error
    if pow(message, e1, n) != c1 % n or pow(message, e2, n) != c2 % n:
        raise ValueError('ciphertexts do not encrypt the same message')
    return message


def parity_recover(n: int, e: int, ciphertext: int, oracle) -> int:
    if n <= 1 or not n & 1 or e <= 0:
        raise ValueError('parity recovery requires an odd RSA modulus and positive exponent')
    low, high = Fraction(0), Fraction(n)
    c = ciphertext % n
    multiplier = pow(2, e, n)
    for _ in range(n.bit_length()+1):
        c = c*multiplier % n
        bit = oracle(c)
        if bit not in {0, 1}:
            raise ValueError('oracle must return plaintext parity 0 or 1')
        middle = (low+high)/2
        if bit:
            low = middle
        else:
            high = middle
    for candidate in range(max(0, math.floor(low)-1), min(n, math.ceil(high)+2)):
        if pow(candidate, e, n) == ciphertext % n:
            return candidate
    raise ValueError('oracle transcript or RSA parameters are inconsistent')


def bsgs(g: int, h: int, modulus: int, order: int, max_steps: int = 100000) -> int | None:
    if modulus <= 1 or order <= 0 or math.gcd(g, modulus) != 1:
        raise ValueError('valid group modulus/order and invertible generator required')
    steps = math.isqrt(order)+1
    if steps > max_steps:
        raise ValueError('BSGS memory/work budget exceeded; factor order or reduce interval first')
    table, value = {}, 1
    for j in range(steps):
        table.setdefault(value, j)
        value = value*g % modulus
    factor = pow(g, -steps, modulus)
    value = h % modulus
    for i in range(steps+1):
        if value in table:
            candidate = i*steps+table[value]
            if candidate < order and pow(g, candidate, modulus) == h % modulus:
                return candidate
        value = value*factor % modulus
    return None


def reused_ecdsa_nonce(order: int, r: int, s1: int, s2: int, h1: int, h2: int) -> tuple[int, int]:
    if order <= 1:
        raise ValueError('invalid subgroup order')
    k = (h1-h2)*pow(s1-s2, -1, order) % order
    d = (s1*k-h1)*pow(r, -1, order) % order
    if (s2*k-h2-r*d) % order:
        raise ValueError('signature relation failed')
    return k, d


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['root', 'crt', 'common-modulus', 'bsgs'])
    parser.add_argument('input', type=Path, help='JSON object of parameters named as in the function signatures')
    args = parser.parse_args()
    try:
        values = json.loads(args.input.read_text(encoding='utf-8'))
        function = {'root': integer_root, 'crt': crt, 'common-modulus': common_modulus, 'bsgs': bsgs}[args.operation]
        print(json.dumps({'result': function(**values)}))
        return 0
    except (ValueError, TypeError, OSError) as error:
        parser.error(str(error))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
