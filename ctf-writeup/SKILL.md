---
name: ctf-writeup
description: "Create a concise reproducible CTF writeup for submission or handoff after a solve. Use only when a writeup is requested; ordinary solves report a short proof path."
license: MIT
compatibility: Local solve artifacts and a verified result.
---

# Write the requested CTF solution

Read the description, solve/STATE.md, solver scripts and actual verification evidence. Reproduce feasible local steps; distinguish observed behavior, inference, unintended solve and unverified claims. If the flag was not verified, say so explicitly and record the blocker. Use [the existing submission template](triage-reference.md) where its sections fit the request.

Lead with the challenge, core primitive and result. Explain the clue, cheapest discriminator, prerequisites and short chain. Include exact commands, relevant tool/runtime versions, script paths, expected output and failure/pivot conditions. Link external sources used without copying them. Historical writeup research is permitted for repository enrichment; do not search exact active solutions while preparing a live-competition solve.

Do not contact or submit to CTFd, scoreboard or organizer APIs automatically. Keep the writeup within the supplied challenge instance boundary; include shared-boundary or expiry evidence when it affected the solve. Do not expose tokens, passwords, instance IDs or unrelated secrets; retain the requested flag in the competition writeup, not reusable learning records.

Write one Markdown artifact in output/ (or the user's chosen path) and report it concisely. After a verified solve capture novel reusable methodology with the existing [learning pipeline](../docs/LEARNING.md), never the flag. Never auto-push.
