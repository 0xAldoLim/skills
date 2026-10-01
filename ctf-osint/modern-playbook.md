# ctf-osint modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Video frame reveals a public URL

**Signal / prerequisite:** Lyrics or narration specifically reference a visible forum page.
**Cheapest useful test:** Inspect key frames at the hinted timestamp and OCR the screen.
**Primitive and method:** Correlate transcript and frame evidence, then visit the public linked page; preserve timestamp and URL provenance.
**Failure / wasted work:** Transcripts alone omit screen-only clues; ask for one ambiguous glyph if targeted OCR fails.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; ffmpeg key frames and OCR.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/f2797a33d8f5851508f37e854afceedf85eee8a3/osint/back-to-the-jungle/solve/WRITEUP.md).

## Regional sighting map beats generic image search

**Signal / prerequisite:** A regional place name and unusual sculpture appear in the description/image.
**Cheapest useful test:** Search the named local authority and its public sighting map.
**Primitive and method:** Use place-specific terms and public map layers, then match roadside features and coordinate precision to the requested answer.
**Failure / wasted work:** Search geography/language biases results; a region match is not an exact-object match.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/f2797a33d8f5851508f37e854afceedf85eee8a3/osint/they-re-making-decoys/solve/WRITEUP.md).

## Unlisted collaboration exposed by public activity

**Signal / prerequisite:** A challenge-created music profile hints at constant listening and a hidden collaboration.
**Cheapest useful test:** Read linked public account metadata and verify activity visibility.
**Primitive and method:** Distinguish unlisted from private objects. Inspect permitted public activity for the collaboration link without contacting the identity.
**Failure / wasted work:** Historical platform features can change; lack of activity is not proof of privacy bypass.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; public page/API metadata when available; narrow human-assisted activity lookup.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/sigpwny/UIUCTF-2024-Public/blob/073cb80f1f42669252e88020fdb5b281f031c693/challenges/osint/the-weakest-link/challenge/SOLVE.MD).

## Endorsements disclose an identity edge

**Signal / prerequisite:** Connections are hidden but endorsements and profile links are public.
**Cheapest useful test:** Inspect public endorsements and contact metadata.
**Primitive and method:** Follow an evidenced relationship rather than enumerating usernames indiscriminately; record each edge and its independent corroboration.
**Failure / wasted work:** A name collision is insufficient; real identities are not permission for private account access.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/sigpwny/UIUCTF-2024-Public/blob/073cb80f1f42669252e88020fdb5b281f031c693/challenges/osint/an-unlikely-partnership/challenge/SOLVE.md).

## Historical address and current object disagree

**Signal / prerequisite:** A bridge/heritage clue leads to a building with inconsistent street numbers.
**Cheapest useful test:** Check a dated authority publication against current property evidence.
**Primitive and method:** Keep a candidate table with source date, street number and requested time frame; resolve historical versus current addressing with independent evidence.
**Failure / wasted work:** A precise-looking old address may answer the wrong time frame.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; dated evidence table and document text search.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/osint/LoveGranniE/solve/WRITEUP.md).

## Unique shop separates chain-store geolocation candidates

- **Signal:** A streetscape contains several chain stores plus one independent business.
- **Cheap test:** OCR/transcribe signage and distinguish unique businesses from multibranch chains.
- **Method:** Use the independent business as a location anchor, then compare neighboring facades and street geometry against a dated map view. Normalize names only after visual confirmation.
- **Failure / pivot:** A branch-name match is insufficient; retain competing towns and avoid contacting people.
- **Verification:** Record the public evidence chain and matching scene features. Source reviewed; challenge not locally reproduced.
- **Source:** [Team pulupuluultraman / Jerit3787, Mynz, Rizzykun; Siber Siaga CTF 2025 Finals](https://ctf.danplace.tech/posts/siber-siaga-ctf-finals-2025/)
