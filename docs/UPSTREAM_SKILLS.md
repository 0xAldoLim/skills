# Upstream skills integration

Source: [`ljagiello/ctf-skills`](https://github.com/ljagiello/ctf-skills), MIT.

| Pin | Meaning |
|---|---|
| `e79be2925d1612e8a97070d6201e300286672370` | Skill content previously integrated |
| `a16e19a652606b10952eb42617742bedea9f2497` | HEAD fetched 2026-11-12 |

## HEAD comparison

`git diff --stat e79be292..a16e19a` changes only `evals/package.json` and `evals/package-lock.json` (dependency overrides). There is no new skill taxonomy or reference content to integrate. The previous observed `a16e19a` is still current.

The full taxonomy was reviewed: 12 upstream skills (the same nine CTF categories plus `solve-challenge`, `ctf-writeup` and `ctf-similar-search`). Local `ctf-common` is an independent addition.

## Previously integrated

| File | Reason |
|---|---|
| `ctf-reverse/radare2-r2pipe.md` | Scripted radare2, patching, ESIL and r2ghidra workflows |
| `ctf-reverse/mba-simplification.md` | msynth/SiMBA workflow with mandatory equivalence checking |
| `ctf-reverse/tools-mcp.md` | IDA/Ghidra/JADX MCP reference; no executable integration |
| `ctf-pwn/attack-playbook.md` | Route selection from recon to leak/control-flow technique |
| `ctf-pwn/static-signals.md` | Static-signal triage linked from the playbook |
| `ctf-pwn/scripts/*.py` | Reviewed payload templates; localhost defaults, explicit remote opt-in |

All copied content remains upstream-attributed and MIT-licensed. Scripts retain a safety header and `scripts/README.md` contract.

## Reviewed, not imported

- `ctf-pwn/pwnable-tw/` (43 challenge writeups, ~12k lines): the underlying primitives are already covered by the local heap, ROP, FSOP, kernel and sandbox references. Importing challenge-specific writeups would add substantial context without a demonstrated capability gain, and would duplicate protected material.
- `ctf-misc/audio.md`: local `ctf-forensics/signals-and-hardware.md`, `stego-advanced.md` and `ctf-misc/encodings-advanced.md` already cover Morse/SSTV/spectrogram/DTMF-style workflows.
- `ctf-similar-search/`: requires a Tavily API key and retrieves external writeups. It would authorize exact-solution lookup and network access outside the owner's live-solve rules. Rejected.
- Upstream `evals/`: upstream-specific evaluation fixtures; not part of the runtime skill corpus.

## License and notices

MIT license and copyright notice are retained in `LICENSE`. Individual imported files keep their upstream provenance. New references are independently written paraphrases or original work; no third-party exploit code was copied into them.
