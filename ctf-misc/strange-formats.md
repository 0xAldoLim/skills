# Strange formats, invented languages and transformations

Use for challenges that do not fit a standard category: invented encodings, custom compression, esolangs, visual/data puzzles, protocol state machines, unusual substitution systems and nonstandard file structures.

## First pass

- `file`, magic/header hex, size, entropy, embedded signatures.
- Printable runs, delimiters, repeated blocks, length fields, checksums.
- Input/output pairs; one-byte changes; fixed points; alphabets.
- What consumes the artifact and what counts as success.

Do not run a dozen decoders blindly. Let the structure choose the next test.

## Transformation inference

| Signal | Try |
|---|---|
| Uniform alphabet, fixed block | Substitution/permutation; frequency and known plaintext |
| Length changes predictably | Encoding/compression; test exact decoder and round-trip |
| Repeating key-like pattern | XOR/stream; derive keystream from known plaintext |
| Grid/pixel structure | Bitplanes, channels, palette, glyph segmentation |
| Numeric sequence | Small cases, recurrence, OEIS, modular pattern |
| Stateful rules | Build a transition table; trace one short run |
| Grammar-like text | Tokenize, infer grammar, write a parser/executor |
| Audio/signal | Plot waveform/spectrum; test baud, alphabet, framing |

## Invented languages and esolangs

1. Collect every token and delimiter; note case/whitespace significance.
2. Identify the instruction/operation set from repeated patterns.
3. Write a parser that accepts all supplied programs.
4. Execute a tiny program by hand; compare with the challenge output.
5. Implement the interpreter/compiler only for the needed subset.
6. Validate on a held-out program.

Common traps: the language is a known esolang with renamed symbols; the “compiler” is a substitution into another language; the program's output is the flag but the interpreter has a hidden opcode. Check for unused opcodes and out-of-band data.

## Custom compression

Look for a header, symbol table, block lengths and literal/back-reference split. Decode one block and verify its length. If the stream is arithmetic/range-coded, recover the probability model from the header or known plaintext. If the format is a container, parse the directory before decompressing members.

## Visual and geometric puzzles

Separate channels and bitplanes; inspect alpha, palette, EXIF and appended data. For jigsaw/shredded images, use edge matching or a solver with a clear objective. For QR/data grids, reassemble the grid before decoding, then verify the error-correction level. For maps/geometry, test scale, rotation, mirror and projection.

## Protocol puzzles

Capture one complete exchange, label frames and state transitions, and replay locally. Change one field at a time. Look for length/type confusion, missing state checks, sequence-number reuse and parser disagreements. Do not attack shared infrastructure.

## Constraints and games

Encode only the decisive constraints. Solve a tiny instance exhaustively, then scale with Z3/SAT/ILP. Validate the model against the game's rules and a held-out state. For game AI, find the win condition and the smallest state change; patching or replaying may be cheaper than search.

## Verification

A decoded string is a candidate. Verify with a round-trip, the original interpreter/game, the challenge checker, or a derivation that does not embed the candidate. Record the transformation and one reproducible command.
