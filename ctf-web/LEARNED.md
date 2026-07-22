# Append-only Learned Techniques

Generated entries are appended after verification. Existing entries are never replaced.

## Java char-to-byte narrowing as a normalization bypass

**Added:** 2026-07-22

**Source:** external_enrichment — yaklang/hack-skills@c9a4b9ee8645eb60763eb4eef172f1ecb0a5b3e8:skills/ghost-bits-cast-attack/SKILL.md (MIT)

**Confidence:** high

**Trigger conditions**

- A Java component validates a Unicode string before writing it through an API that keeps only each character's low byte.
- A filter blocks literal ASCII separators, metacharacters, or control bytes but the downstream parser still receives them.

**Core insight**

Validation and execution can see different bytes when a Java UTF-16 code unit is narrowed without an explicit charset conversion. The bypass is the representation disagreement, not the downstream injection family itself.

**Technique**

Trace the value from validation to serialization. If a cast, low-byte mask, write(int), or writeBytes-style path truncates UTF-16 code units, generate Unicode candidates whose low byte equals the required ASCII byte. Confirm the exact normalization locally before sending one minimal authorized probe.

**Commands or code**

```text
def low_byte_char(target, high=1):
    value = ((high & 0xff) << 8) | (target & 0xff)
    if 0xd800 <= value <= 0xdfff:
        raise ValueError('avoid surrogate code units')
    return chr(value)
```

**Verification evidence**

Pinned source methodology was compared against the full local Markdown corpus; searches found Unicode cases but no low-byte narrowing route. The distilled generator follows the byte identity low_byte(chr((k << 8) | target)) == target.

**Resulting primitive**

A filtered ASCII byte appears after a Java string-to-byte boundary, enabling a separately verified injection primitive.

**Failure modes**

- UTF-8 encoding is applied correctly before the sink.
- The chosen code point is normalized, rejected, or is a surrogate.
- The downstream parser never interprets the reconstructed byte as syntax.

**When not to use**

- The backend is not Java or there is no narrowing boundary.
- A literal payload already works.
- The only evidence is a generic WAF block with no representation mismatch.

## HTTP/2 downgrade desynchronization as a request-smuggling variant

**Added:** 2026-07-22

**Source:** external_enrichment — yaklang/hack-skills@c9a4b9ee8645eb60763eb4eef172f1ecb0a5b3e8:skills/request-smuggling/SKILL.md (MIT)

**Confidence:** high

**Trigger conditions**

- The edge accepts HTTP/2 while the origin receives reconstructed HTTP/1.1.
- Header normalization, duplicate handling, pseudo-header mapping, or body framing differs across the downgrade boundary.

**Core insight**

HTTP/2 has different framing and header rules; a proxy that reconstructs HTTP/1 can create a second parser view even when the client never sent an HTTP/1 request.

**Technique**

Establish a normal H2 request and compare what the origin receives. Test one controlled discrepancy at a time: duplicate length metadata, forbidden hop-by-hop fields, pseudo-header ordering, or abnormal path translation. Confirm a boundary disagreement with isolated requests before attempting any chain.

**Commands or code**

```text
# Use an isolated lab or challenge instance.
# Capture one baseline H2 request, then vary a single translation input.
curl --http2-prior-knowledge -i https://target.example/
```

**Verification evidence**

The local corpus includes an HTTP/1 cache-proxy desync technique but contains no H2.CL, H2.TE, pseudo-header, or downgrade-smuggling entry. The pinned source explicitly separates this variant from classical CL.TE/TE.CL.

**Resulting primitive**

A request-boundary disagreement between the edge and origin during H2-to-H1 translation.

**Failure modes**

- The edge and origin both enforce strict H2 translation.
- The connection is not reused.
- Observed errors come from ordinary header rejection rather than boundary disagreement.

**When not to use**

- The service is HTTP/1 end to end.
- The challenge provides no proxy or translation layer.
- Testing could affect unrelated users; use an isolated instance or do not proceed.
