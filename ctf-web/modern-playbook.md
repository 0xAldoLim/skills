# ctf-web modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Signed token length truncation

**Signal / prerequisite:** A length field is narrow but the serializer writes the full string.
**Cheapest useful test:** Round-trip a local long string at the field-width boundary.
**Primitive and method:** Compare the signed byte stream with decoded identity, eight-byte expiry and admin fields. Obtain a legitimately signed stream whose trailing bytes become different fields.
**Failure / wasted work:** A strict full-length decoder or fixed serialization eliminates the primitive. MAC forgery is unnecessary.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/web/gomail/solve/WRITEUP.md).

## HTML namespace mutation after sanitization

**Signal / prerequisite:** Sanitized DOM is serialized and parsed again in a template context.
**Cheapest useful test:** Serialize/reparse an inert MathML/SVG marker in the exact bot browser.
**Primitive and method:** Record namespace and node changes across the sanitizer and insertion step before testing executable content inside the assigned challenge.
**Failure / wasted work:** Browser and sanitizer versions, blocked element names and sink context matter; old payload strings may be obsolete.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; local browser DOM snapshots and one discriminating bot test.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2025_Public/blob/f423ae945ddb8370bbb4ca86c425dd8b9ed6a33b/web/mutant/solve/WRITEUP.md).

## Framework behavior instantiated from attributes

**Signal / prerequisite:** A Yii component accepts attacker-supplied configuration through setAttributes.
**Cheapest useful test:** Inspect the exact Yii version and instantiated class/property path.
**Primitive and method:** Identify a reachable behavior/configuration gadget, then prove a harmless local output/path change. Follow the resulting file-write primitive only inside the challenge.
**Failure / wasted work:** The published version-specific gadget requires its component and setters; arbitrary class names alone are insufficient.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/ctf-gemastik/penyisihan-2024/blob/b5800ac9f044bd43056b3251fe1b51eb135969e4/web/vendor-baru/writeup/README.md).

## Prototype properties excluded from signatures

**Signal / prerequisite:** Prefix-stripped fields enter an ordinary object; HMAC uses Object.entries while downstream reads inherited properties.
**Cheapest useful test:** Compare own-property enumeration and inherited lookup with inert outputPrefix data.
**Primitive and method:** Keep the original signed own fields while testing whether __proto__ supplies an unsigned downstream property. Verify each subsequent file/path/runtime condition independently.
**Failure / wasted work:** Null-byte file behavior is Bun-version-specific; the published unbounded crash request is not an acceptable generic probe.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/f2797a33d8f5851508f37e854afceedf85eee8a3/web/prisoner-processor/solve/WRITEUP.md).

## Class pollution changes nonce and template policy

**Signal / prerequisite:** Recursive object merging reaches class init globals and template settings.
**Cheapest useful test:** Trace the merge into one harmless local global and observe it.
**Primitive and method:** Confirm the reachable global controls; then reproduce deterministic nonce generation and the template-environment refresh in the supplied app before a bot request.
**Failure / wasted work:** Turning a flag endpoint off does not repair class pollution; CSP and HttpOnly remain separate requirements.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/DownUnderCTF/Challenges_2024_Public/blob/f2797a33d8f5851508f37e854afceedf85eee8a3/web/co2v2/solve/WRITEUP.md).

## PHP query arguments enter framework configuration

**Signal / prerequisite:** A framework CLI/config parser runs under a web SAPI with register_argc_argv enabled.
**Cheapest useful test:** Inspect php.ini/SAPI and one harmless argv/config parse locally.
**Primitive and method:** Trace request-to-argv and template-path configuration; verify wrapper access, file checks and loader behavior independently before exploiting the assigned app.
**Failure / wasted work:** Configuration and SAPI are essential; FTP reachability does not itself imply code execution.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** medium; local request/config replay.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://vicevirus.github.io/posts/wgmy-2024-web-writeup/).

## Ambiguous concatenation collapses sandbox origins

- **Signal:** A sandbox origin hashes concatenated body, product, origin and trailing salt.
- **Cheap test:** Construct two harmless field tuples with identical concatenation in a local harness.
- **Method:** Trace controllable boundaries and the navigation-to-salt race; validate origin/source checks and blob access on a local replica before the assigned bot test.
- **Failure / pivot:** This is ambiguous encoding, not a SHA-256 collision. Historical third-party XSS examples do not authorize testing that service; use an owned permitted origin.
- **Verification:** Assert equal hash inputs and demonstrate same-origin access only inside the dedicated reproduction. Source reviewed; challenge not locally reproduced.
- **Source:** [terjanq / Google CTF; Google CTF 2024 Quals](https://github.com/google/google-ctf/blob/1655538e8c8b41451d39f670ef15a5af22979ca9/2024/quals/web-postviewer3/README.md)
