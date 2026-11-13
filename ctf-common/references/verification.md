# Verification and flag provenance

A flag-shaped string is a candidate. Success requires support that does not depend on the candidate itself.

## Provenance ladder

| Rank | Origin | Meaning | Can declare success alone? |
|---:|---|---|---|
| 1 | Commitment/oracle | Operator-supplied digest, challenge-native checker, or authenticated response that contains the value | Yes, with the exact evidence recorded |
| 2 | Derivation | Reproducible computation from supplied artifacts and recovered parameters | Yes, if the derivation replays from clean inputs |
| 3 | Runtime/service | Value read from the assigned instance through a demonstrated primitive | Only when the response is authenticated/expected and the path is explained |
| 4 | Structural | Decoded from an artifact transform with a verified key/format | Rarely; confirm with a checker or independent re-derivation |
| 5 | Static string | README, comment, `strings`, source constant, test fixture | No |
| 6 | Guess/model/scanner | Pattern match, prior knowledge, "looks like a flag" | No |

`FLAG{test}`, `flag{example}`, `fake`, `dummy`, `placeholder`, `sample`, `changeme` and values in tests/docs are decoys until the challenge's runtime or checker says otherwise.

## Independent verification

Use at least one of:

- **Challenge checker:** run the supplied validator/`readflag` locally or against the assigned instance, with a clean environment. Inspect what it checks; a checker that always accepts is not evidence.
- **Derivation replay:** write a small script from the description and artifacts that recomputes the plaintext/flag from scratch. It must not embed the candidate as an input.
- **Operator commitment:** compare the candidate against a SHA-256 digest supplied by the operator, not by a challenge artifact.
- **Authenticated service response:** a response from the assigned challenge whose semantics include the value (for example, a privileged page or a verified API response). A 200 status alone is not proof.
- **Platform acceptance:** only when the operator explicitly requested submission. Submission is not part of ordinary solving.

Record the method, command, artifact hashes and observed result. Keep the candidate and the evidence separate.

## CTF-ABACUS provenance lesson

A recovered flag can come from intended exploitation, direct exposure, memorized recall, external lookup, guessing or an unsupported claim. Track the first point where the value appeared and the action that produced it. If the value appeared in a README before any exploitation, label it static. If it appeared only after a reproduced exploit, label it runtime/derived. Do not collapse both into "solved".

## False-positive discipline

Do not reject a candidate merely because it looks unusual. Verify it. Do not reject a line because a scanner flagged it. Inspect the source and the checker. Conversely, do not accept a candidate because it has the right format or because a tool says "verified".

## Handling multiple candidates

Rank by provenance, then by how directly the value is tied to the intended primitive. Preserve the others with their origin in the evidence ledger. Report the highest-confidence candidate and state exactly why it is valid. If two candidates remain plausible and no independent oracle exists, report the ambiguity rather than inventing certainty.

## State helper

```bash
python3 ../../scripts/ctf_state.py candidate --dir solve --value 'FLAG{candidate}' --origin static
python3 ../../scripts/ctf_state.py verify --dir solve --candidate C1 --method checker \
  --command './check_flag < candidate.txt' --result 'accepted: exit 0, expected digest matched'
python3 ../../scripts/ctf_state.py status --dir solve
```

Rejected verification methods include `claim`, `format`, `regex`, `scan`, `readme`, `model` and `tool`. A static origin does not prevent later verification; it prevents treating the static string as already verified.
