# Upstream skills integration

Source: [`ljagiello/ctf-skills`](https://github.com/ljagiello/ctf-skills)
commit `e79be2925d1612e8a97070d6201e300286672370` (MIT).
Owner checkout before integration: `1d51e0f4a289cb1b6e7326d41db4e6f6ad54516d`.

## Integrated after review

| File | Reason |
| --- | --- |
| `ctf-reverse/radare2-r2pipe.md` | Scripted radare2, patching, ESIL and r2ghidra workflows not covered by the existing reverse references |
| `ctf-reverse/mba-simplification.md` | Concrete msynth/SiMBA workflow and mandatory equivalence checking |
| `ctf-reverse/tools-mcp.md` | IDA/Ghidra/JADX MCP reference; no executable integration is enabled automatically |
| `ctf-pwn/attack-playbook.md` | Route-selection view from recon to leak/control-flow technique |
| `ctf-pwn/static-signals.md` | Static-signal triage linked from the playbook |
| `ctf-pwn/scripts/*.py` | Reviewed payload templates; localhost defaults, explicit remote opt-in |

All copied content remains upstream-attributed and MIT-licensed. The scripts
received a safety header and a `scripts/README.md` contract.

## Rejected

- `ctf-similar-search/`: requires a Tavily API key and retrieves external
  writeups. It would authorize solution lookup and network access outside the
  owner's scope rules. The owner's research broker and scope policy take
  precedence.
- Upstream `evals/`: evaluation fixtures are upstream-specific and are not part
  of the runtime skill corpus.

## Retrieval

`scripts/rebuild_indexes.py` routes r2pipe, MBA, MCP, and Linux exploit-route
signals to the new references. The scripts are discoverable through the pwn file
catalog and are never run automatically.
