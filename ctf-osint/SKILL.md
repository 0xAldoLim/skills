---
name: ctf-osint
description: "Solve CTF public-source identity, location and historical evidence puzzles. Use for geolocation, reverse image search, map/satellite correlation, public profiles, archives, DNS/CT, metadata, transport/public records and cross-source verification. Do not actively test discovered infrastructure."
license: MIT
compatibility: "Agent Skills compatible host (OpenCode, Codex CLI, Claude Code, or similar) with Python 3 and a shell; network access to public sources; tools install on demand."
metadata:
  user-invocable: "true"
  version: "2.0"
---

# ctf-osint

Read the [shared contract](../ctf-common/SKILL.md) once: scope, untrusted content, FAST/EXPERT routing, evidence, verification, state. If this skill is invoked directly, load it before acting.

## Triage from evidence

Extract image metadata, text, crop clues, timestamps, usernames and identifiers before searching. Maintain an evidence chain with query, source, capture/publication date, inference and confidence. Exact answer verification is usually multi-source consistency, not a flag-looking string.

| Evidence | Cheapest discriminator | Reference |
|---|---|---|
| Landmark, road, logo or historical photo | Metadata/OCR and reverse image; combine visual constraints and local language | [Geolocation](geolocation-and-media.md), [modern cases](modern-playbook.md) |
| Username, reused avatar, platform ID | Public profile and archive comparison, not login/password testing | [Social](social-media.md) |
| DNS/WHOIS/CT, Git history or archived pages | Passive record/export/history lookup; confirm the relevant date | [Web/DNS](web-and-dns.md) |
| Aircraft, vessel, transport or public records | Correlate identifier, route and time zone with documented provenance | [Detailed triage](triage-reference.md) |
| Satellite imagery, maps, obscure geography | Match road/terrain/coastline geometry, shadows and seasonal cues; verify at multiple scales | [Verification](verification-and-ethics.md), [geolocation](geolocation-and-media.md) |

## Execute cheaply

Use English, Indonesian and Malay query variants when geography warrants them; preserve original spellings. Treat OCR and reverse-image results as candidates. Street numbering, renamed venues, timezone conversions and archival timestamps can differ: verify the requested time period and object. Do not mass-enumerate users or test discovered hosts.

A visual handoff must include the crop, candidate locations, a concrete distinguishing feature and the exact observation requested. Keep searches confined to public, competition-authorized information; do not expose unrelated individuals' private data.

## Verify and finish

Require at least two independent sources for a location/identity, or one authoritative record plus a visual/geometric check. Explain how each clue discriminates. Report the answer, the evidence chain and confidence. Do not present a plausible guess as verified.

## References

[INDEX.md](INDEX.md) for routes and the full catalog. [Verification/ethics](verification-and-ethics.md), [tools](tools-mcp.md), [triage](triage-reference.md). Load one to four matching sections only.
