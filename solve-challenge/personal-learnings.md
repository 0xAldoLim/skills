# Personal verified challenge learnings

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-19

- If a challenge advertises one flashy component as the obvious target, check the surrounding shell, companion artifacts, and alternate surfaces in parallel. The intended centerpiece may be a decoy while the enclosing app, archive chain, or side-channel path is easier and more real.
- When two artifacts appear to describe the same object at different stages, test simple transforms and correlations first: paired plaintext/ciphertext assets, stub-stage versus payload-stage files, image markers that select packets, or logs that index into structured data.
- For binaries and APKs that look too small or too trivial, check for nested payloads, tail-appended blobs, packed secondary artifacts, or delimiter-encoded data in slack space before spending time on the visible wrapper logic.
- In hybrid web-plus-crypto challenges, treat auth tokens and signature wrappers as data-leak surfaces, not just things to forge at the end. Source review and sample collection often reveal that one verifier ignores fields that another verifier depends on.
- In kernel or low-level targets, classify the primitive before committing to exploitation. A suspicious ioctl may be a fixed-path disclosure with clamped output semantics rather than a corruption bug.

