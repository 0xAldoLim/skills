# Unfamiliar challenges and novel problems

Use this when no known technique cleanly applies. The method is general; do not memorize a solution.

## 1. Characterize the artifact

- `file`, magic bytes, header hex, size, entropy and embedded signatures.
- Strings, symbols, imports, sections, chunks, records, timestamps and version fields.
- Input/output lengths and alphabets; repeated blocks; delimiters; checksums.
- What produced it, what consumes it, and what the challenge actually validates.

Extensions are hints, not truth. A file named `.jpg` can be a ZIP, a VM bytecode or a text transform.

## 2. Infer the transformation

Collect at least two input/output pairs. Ask:

- Is the output a permutation, substitution, arithmetic function, encoding or compression?
- Does length grow, shrink or stay fixed? Which bytes/characters are preserved?
- Is it deterministic? Does a one-byte change produce a local or global change?
- Are there fixed points, invariants, linearity, cycles or block boundaries?
- Does a known plaintext, header or flag prefix appear after a guessed inverse?

Build the smallest reversible model and test it on a third pair before scaling.

## 3. Reconstruct the format or machine

- Identify fields and boundaries from repeated structures and offsets.
- Build a parser that round-trips a supplied sample.
- For a VM: trace one short input, recover opcodes, stack/register effects and control flow.
- For a protocol: capture one complete exchange, label frames and state transitions, replay locally.
- For a game: find the win condition and the smallest state change that reaches it.
- For a constraint system: encode only the decisive constraints, solve, then validate in the original checker.

## 4. Choose the cheapest experiment

| Question | Cheap experiment |
|---|---|
| Is this an encoding or compression? | Try exact known decoders; compare header/length; test a sample round-trip |
| Is this a custom cipher? | Differential one-byte changes; known plaintext; linearity/invariant test |
| Is this a VM/interpreter? | Trace one instruction; dump state; patch one opcode |
| Is this a parser bug? | Compare two parsers or two lengths/encodings on the same input |
| Is this a math puzzle? | Compute small cases, look up the sequence, test the recurrence |
| Is this a signal? | Plot time/frequency; test baud, alphabet and framing hypotheses |
| Is this a protocol? | Replay a recorded exchange with one field changed |

## 5. Use the right generic tool

- Exact arithmetic: Python integers, `gmpy2`, `sympy`.
- Constraints: Z3 for finite domains; validate the model on known cases.
- Symbolic execution: angr/Triton only on a bounded slice with modeled input.
- Emulation: Unicorn/Qiling for a decisive routine, not the whole system.
- Search: `rg` over source, strings, symbols and extracted metadata.
- Research: official format specs, RFCs, papers, source code and vendor docs.

## 6. Validate, don't assume

A model that explains two samples can still be wrong. Test predictions on held-out samples, edge cases and the original checker. If the challenge validates a flag, use that validator; if it validates behavior, replay the behavior from a clean state.

## Worked mini-examples

**Invented language.** Extract the token alphabet, identify delimiters and repeated structures, hypothesize a grammar, and write a parser that accepts all supplied programs. Then execute one program by hand and compare with the challenge output.

**Custom compression.** Look for a header, a length table and a literal/back-reference split. Decode one block, verify the length, then generalize. If the stream is arithmetic-coded, recover the probability model from the header or known plaintext.

**Visual puzzle.** Separate the image into channels/bitplanes, inspect EXIF and alpha, test rotations/flips, and extract repeated glyphs. Do not run twenty stego tools blindly; choose based on the format and the observed anomaly.

**Math sequence.** Compute the first small terms, search OEIS or the challenge's own recurrence, then prove or test the closed form on a held-out term.

## Stop rules

- Two changed experiments with no new discriminating evidence: change representation or ask for the smallest human observation.
- A decoy route with no corroboration after two cheap probes: return to the intended primitive.
- A model with too many free parameters: reduce the model or gather a stronger observation.
