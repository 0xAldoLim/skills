# Personal verified challenge learnings

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-19

- **Custom interpreter may be a decoy:** If a challenge heavily spotlights a custom interpreter or relay, inspect the surrounding app shell in parallel. Page-specific bundles, RSC surfaces, and client-side auth logic can show that the interpreter is real but low-value while the actual bug sits in the enclosing app.
- **Parser-fingerprint before exploitation:** For custom reference or expression interpreters, run a compact live parser matrix first. Include canonical references, malformed numeric forms, bracket syntax, and any claimed dereference operator using fully controlled local objects so you can separate grammar behavior from challenge data.
- **Order-sensitive duplicate-cookie bypass:** Exact-match auth gates may still accept duplicate cookie names if the framework merges them in order and the valid value wins late. Replay with invalid-first and valid-last cookie pairs before assuming the cookie check is strict.
- **Non-serializable live results can persist:** A relay slot that serializes as `null` or `{}` can still hold a useful live object for later operations. Probe later-slot metadata and behavior before deciding a value is dead just because its serialized form is empty.
- **Literalization boundaries matter:** `$N`-style tokens embedded inside object or array literals may remain literal strings instead of becoming references, and self-referential structures may not create a local binding context. Prove which contexts actually trigger reference resolution before building deeper chains.
- **Index parsing can normalize strange prefixes:** Custom parsers may accept decimal-prefix forms like `$1abc`, `$1e3`, `$0x0`, `$+1`, or `$-0` while still treating named roots like `$flag` or `$process` as index errors. Map the tokenizer instead of trusting comments or client notes.
- **Single-root versus multi-root parsing:** Strings with multiple `$` markers may still resolve only one root token. Test concatenated, spaced, and dot-spliced forms explicitly rather than assuming repeated expansion.
- **Built-in graph confinement is useful evidence:** Property access and type hops that only yield more built-ins (`Number`, `Boolean`, `Function`, stock methods) are evidence that the object graph is confined. Establish that limit early so you stop overinvesting in dead-end constructor walks.
- **Aliasing does not imply autovivification:** A reference alias can point at the same visible object value while missing-property reads still fail to create nested structure. Test aliasing and structure creation separately.
- **RSC-looking colon tails may be fake syntax:** Tokens that look like `"$0:f:..."` may collapse to the base object or be parsed as part of the index token rather than introducing a second traversal language. Verify the live grammar before assuming framework-inspired semantics.
- **Probe for hidden prefix slots and reuse stability:** Minimal arrays, off-by-one references, and repeated same-pass reuse can show whether hidden internal prefix slots exist and whether a live object remains stable across later references in the same request.
- **Same-request transport can differ from cross-request memory:** A live object may survive through a later stock-shaped block in the same interpreter pass while all cross-request `$N` state resets on the next HTTP request. Test both scopes separately.
- **Reference-resolved operators may be trusted:** If an operator slot is populated from a previously resolved live reference and still executes like stock vocabulary, treat slot position as part of the trust boundary rather than only the literal string value.
- **Decorative signature plus real MAC:** When a token contains a flashy signature wrapper and a plain MAC, confirm which verifier enforces what. The decorative signature field can leak or carry material later reused by an HMAC-based admin or backend verifier.

