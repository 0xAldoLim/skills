# Research foundations

Retrieved 2026-11-12. This page records what was reviewed, what was adopted, and what was deliberately not adopted. It is not a claim that every technique was reproduced.

| Work | Source | Version | License / terms | Adopted |
|---|---|---|---|---|
| OpenCode-for-CTF | [h1kibi/Opencode-for-CTF](https://github.com/h1kibi/Opencode-for-CTF) | `6b432a43dd33edf211865da45ba50b99593408f1` (2026-11-05) | MIT | FAST/EXPERT lanes; evidence-first closure; thin controllers; bounded route budgets |
| D-CIPHER | [NYU-LLM-CTF/nyuctf_agents](https://github.com/NYU-LLM-CTF/nyuctf_agents) | `612190f298ae9e604f00370019beed4ba1f372f6` (2026-07-17) | MIT | Planner/executor separation expressed as one-test-at-a-time evaluation |
| EnIGMA | [arXiv:2409.16165](https://arxiv.org/abs/2409.16165) | ICML 2025 | arXiv paper license | Interactive tooling; grounded observations; hallucinated-observation warning |
| CTFAgent / CTFKnow | [CCSCTF-Web](https://yan5ui.github.io/CCSCTF-Web/) | ACM CCS 2025 | Project page CC BY-SA 4.0; source access separate | Targeted retrieval; environment-feedback adaptation; application is harder than recall |
| PentestGPT | [GreyDGL/PentestGPT](https://github.com/GreyDGL/PentestGPT) | `e8b1bb77d1ac00329675cec3b060aba971ec1ac8` (2026-07-14) | MIT | Durable state, phases, explicit progress |
| CTFusion | [kaist-hacking/CTFusion](https://github.com/kaist-hacking/CTFusion) | `167982004c2eff9975872654ed9e883c7c8f9d52` (2026-06-12) | MIT; vendored components retain their licenses | Independent A/B evaluation, flag provenance; no platform automation |
| AgentLSD | [arXiv:2609.19140](https://arxiv.org/abs/2609.19140) | AISec 2026 | arXiv paper license | Trap taxonomy, task contamination, provenance, bounded decoys |
| CTF-ABACUS | [arXiv:2608.26237](https://arxiv.org/abs/2608.26237) | arXiv 2026 | arXiv paper license | Flag provenance and demonstrated-exploitation distinction |
| Arditi et al. | [arXiv:2406.11717](https://arxiv.org/abs/2406.11717) | arXiv 2024 | arXiv paper license | Background only; no refusal bypass or capability claim |
| Gray Swan indirect prompt injection | [Gray Swan research](https://www.grayswan.ai/research); [arXiv:2603.15714](https://arxiv.org/abs/2603.15714) | 2026 | arXiv paper license | Concealment; inspect tool actions/side effects, not only the final response |
| HackSynth | [aielte-research/HackSynth](https://github.com/aielte-research/HackSynth) | `48a41f795dda186df66561c4fd2b58ae84e3e4f8`; arXiv:2412.01778 | AGPL-3.0; no code copied | Planner/summarizer feedback loop; explicit benchmark budgets |
| ljagiello/ctf-skills | [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) | HEAD `a16e19a652606b10952eb42617742bedea9f2497`; integrated content `e79be2925d1612e8a97070d6201e300286672370` | MIT | Preserved prior imports; reviewed taxonomy; no duplicate pwnable.tw/audio import |
| PRESTIGE | [0xAldoLim/prestige](https://github.com/0xAldoLim/prestige) | reference only | MIT | Evidence, lane and verification concepts; no runtime dependency |

The machine-readable ledger is [knowledge/research-frameworks.json](../knowledge/research-frameworks.json).

## What changed in practice

### OpenCode-for-CTF

The useful part is not the plugin runtime. It is the discipline: a fast lane for clear primitives, an expert lane for complex chains, a candidate/oracle distinction, and small controllers with lazy references. This repository adopts those ideas as a standalone contract. It does not vendor agents, MCP servers, subagent orchestration or tool packs.

### D-CIPHER and EnIGMA

D-CIPHER's planner/executor split is useful when the task is genuinely multi-stage. In a skills-only system, the same benefit comes from one hypothesis, one cheap test and an explicit evaluation of the result. EnIGMA's interactive-tool finding is reflected in the tooling ladder, but the skills do not require a persistent debugger and prefer scripted, reproducible commands. EnIGMA's observation that models can self-generate observations motivates the separation between recorded tool output and model inference.

### CTFAgent / CTFKnow

The paper's practical lesson is that models often know a technique but fail to apply it to the current artifact and fail to adapt after feedback. The skills therefore emphasize evidence-first triage, one cheap discriminator, failure-layer classification and targeted retrieval, rather than larger technique catalogs.

### PentestGPT and CTFusion

PentestGPT contributes durable task state and progress evaluation. CTFusion contributes independent comparison and flag provenance. This repository implements a compact state ledger and deterministic tests; it does **not** include CTFd integration, live competition submission, or a claim of benchmark superiority. A reproducible A/B/C protocol is documented in [EVALUATION.md](EVALUATION.md); no paid model run was performed for this overhaul.

### AgentLSD and CTF-ABACUS

AgentLSD's five trap families (goal hijack, false authority, false validation, exploration bait, time sink) are the basis of [ctf-common/references/adversarial-content.md](../ctf-common/references/adversarial-content.md). The scanner and ledger are advisory safeguards, not a claim of immunity. CTF-ABACUS's provenance distinction prevents a README value, recalled value or unsupported claim from being reported as demonstrated exploitation.

### Arditi et al.

The refusal-direction result is background on model internals. It is **not** implemented as an attack, an abliteration recipe, or a way to bypass provider controls. Authorized analysis of malicious CTF artifacts is supported by instruction-source separation and scope rules, not by disabling model safety.

### Gray Swan indirect prompt injection

The large-scale competition study separates an attack's effect from its visibility: an agent can execute a harmful action while its final answer looks clean. The skills therefore treat a clean final message as insufficient evidence and require the recorded tool call, side effect or checker observation. This is a provenance rule, not a claim that any model is immune.

### HackSynth

HackSynth's planner/summarizer split reinforces the value of reducing tool feedback into a compact fact before the next step. This repository implements that as a state/evidence discipline, not as a two-model runtime. Its AGPL code was not copied.

### ljagiello/ctf-skills

`a16e19a` differs from the previously integrated `e79be292` only in `evals/package.json` and `evals/package-lock.json`. No skill taxonomy or reference content changed. The upstream `ctf-misc/audio.md` and `ctf-pwn/pwnable-tw/` tree were reviewed; their primitives are already covered by local references and importing 12k lines of challenge-specific writeups would add cost without a clear capability gain. `ctf-similar-search` remains rejected: it requires an external API key and retrieves exact writeups, which conflicts with live-solve discipline.

## Method notes

- Repository HEADs were fetched with `git ls-remote` and cloned; code and prompts were inspected, not only READMEs.
- Papers were read at abstract/HTML level. Claims about their experiments are reported as the authors' findings, not independently reproduced here.
- No upstream prompt, trap implementation or exploit code was copied into this repository. Imported MIT material retains its notice in [docs/UPSTREAM_SKILLS.md](UPSTREAM_SKILLS.md) and the [NOTICE](../NOTICE.md).
- No model benchmark was run, so no solve-rate, token or elapsed-time improvement is claimed.
