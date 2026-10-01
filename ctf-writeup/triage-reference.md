# Detailed category triage and techniques

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Templates

### Submission Format

```markdown
---
title: "<Challenge Name>"
ctf: "<CTF Event Name>"
date: YYYY-MM-DD
category: web|pwn|crypto|reverse|forensics|osint|malware|misc
difficulty: easy|medium|hard
points: <number>
flag_format: "flag{...}"
author: "<your name or team>"
---

# <Challenge Name>

## Summary

<1-2 sentences: what the challenge was and the core technique. Keep it direct.>

## Solution

### Step 1: <Action>

<Explain the key observation in 3-8 short lines. Keep it direct.>

\`\`\`python
<one complete solving script from provided challenge data to printing the final flag>
\`\`\`

### Step 2: <Action> (optional)

<Only add this when a second short step genuinely helps readability, such as separating the core observation from final verification.>

### Step 3: <Action> (optional)

<Use only if the challenge really needs it. Keep the total number of steps small.>

## Tools and External Resources Used

<List meaningful non-local tools and resources used, including online tools, GitHub repositories, hosted helpers, CyberChef recipes, sandboxes, public lookup services, notebooks, and documentation that materially contributed to the flag. Include the exact tool name and URL when known, what input was provided, what result was used, and whether any sensitive value was redacted. If no external tools were used, say so explicitly.>

## Flag

\`\`\`
flag{example_flag_here}
\`\`\`
```

Guidance:

- Prefer 1-3 short steps total
- Keep code to the smallest complete solving script
- Do not split "recover secret", "derive key", and "decrypt flag" into separate partial snippets
- The script should start from the challenge data and end by printing the flag
- Include external/online tools and GitHub repositories when they contributed to an observation, decoded artifact, deobfuscation result, exploit, or final flag
- Avoid long background sections
- Avoid dead ends unless they explain a key pivot
- Avoid multiple alternative solves; pick one clean path
- Redact the flag only if the user explicitly asks for redaction

---

## Best Practices Checklist

Before finalizing the writeup, verify:

- [ ] **Metadata complete** — title, CTF, date, category, difficulty, points, author all filled
- [ ] **Flag handling matches request** — keep the real flag unless the user asked for redaction
- [ ] **Reproducible steps** — a reader can follow your writeup and reproduce the solution
- [ ] **External tools documented** — online tools, GitHub repositories, hosted helpers, CyberChef recipes, sandboxes, lookups, or notebooks are named with URL/version when known and their contribution is stated
- [ ] **Code is runnable** — exploit scripts include all imports, correct variable names, and comments
- [ ] **No sensitive data** — no real credentials, API keys, or private infrastructure details
- [ ] **Length stays concise** — the writeup is short enough for fast review
- [ ] **Tools and versions noted** — mention specific tool versions if behavior depends on them
- [ ] **Proper attribution** — credit teammates, referenced writeups, or tools that were essential
- [ ] **Grammar and formatting** — consistent heading levels, code blocks have language tags

## Quality Guidelines

**DO:**
- Explain just enough for fast verification
- Include one complete solving path, not multiple alternative routes
- Include one complete script that goes all the way to the final flag
- Include online tools and external repositories that contributed to the solve, including what they were used for
- Show actual output (truncated if very long) to prove the approach worked
- Tag code blocks with language (`python`, `bash`, `sql`, etc.)
- Keep the main path front-loaded so a reader can validate it quickly

**DON'T:**
- Copy-paste raw terminal dumps without explanation
- Paste several partial snippets that force the reader to reconstruct the final solve
- Hide online tools, GitHub repos, hosted helpers, sandboxes, or public lookup services that materially contributed to the flag
- Leave placeholder text in the final writeup
- Include irrelevant tangents that don't contribute to the solution
- Assume the reader knows the specific challenge setup

