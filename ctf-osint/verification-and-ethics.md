# OSINT verification, ethics and cross-source checks

OSINT answers are often a place, person, object or time. A plausible answer is not a verified one.

## Evidence chain

For every claim record:

```text
claim:
source URL:
publisher/author:
publication/capture date:
access date:
what it directly shows:
inference:
confidence: high|medium|low
independent corroboration:
```

Keep original files/hashes. Do not overwrite crops; write derived images to `output/`.

## Cross-source verification

Use at least two independent sources when possible:

1. **Primary record:** official registry, court/transport record, archived page, original post, map data, satellite image.
2. **Secondary corroboration:** reputable reporting, another archive, a matching photo from a different angle/time.
3. **Geometry/temporal check:** road angles, coastline, building footprint, shadow direction, sun position, seasonal vegetation, signage language, vehicle plates, flight/vessel track.
4. **Negative check:** does a candidate explain the *absence* of expected features? Does the date/timezone conversion still fit?

Two pages quoting the same original are one source, not two.

## Geolocation

- Match large geometry first (coastline, rivers, ridges, road network), then local details (signs, poles, storefronts, curb paint).
- Use map/satellite history for renamed or demolished venues.
- Check shadows and sun angle for hemisphere/season/time; confirm with a solar calculator.
- Treat OCR, reverse-image matches and model captions as candidates.
- Verify the requested granularity: country vs city vs exact building.

## Identity and social media

- Correlate usernames, avatars, bios, writing style, timezone activity and linked accounts.
- Prefer public, competition-relevant information. Do not use breached data, password guessing, private accounts or unrelated individuals' personal data.
- Distinguish a namesake from the target with at least one independent link.
- Do not test discovered hosts, credentials or accounts.

## Metadata and archives

Check EXIF/XMP, document authorship, Git history, Wayback/CDX, DNS/WHOIS/CT history, certificate transparency and public caches. Timestamps can be edited; corroborate with content and external records. A deleted post may survive in an archive, but archive date ≠ original date.

## Privacy and scope

Competition-authorized, publicly available information only. Do not expose addresses, phone numbers, private accounts or unrelated personal data in the final answer. If the challenge asks for a person's location, report only the requested granularity.

## Final check

Write the shortest chain from clue to answer and mark which step is inference. If two candidates remain, report both with the discriminating evidence rather than guessing. Do not claim verification from a single image match.
