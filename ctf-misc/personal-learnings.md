# Personal verified challenge learnings

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-23

- **Pyjail debugger escape:** If a Python jail still exposes `breakpoint()` or drops into `pdb`, use the debugger prompt as a second interpreter. From `(Pdb)`, try `__import__("os").system("sh")` or equivalent imports even when the original eval surface looked restricted.

## Local Learnings Appended 2026-04-24

- **Nonstandard base64 chunk widths:** If an encoder looks base64-like but output length grows in 3-character groups instead of 4, map each alphabet char to 6 bits as usual, then regroup the bitstream into 9-bit plaintext chunks rather than 8-bit bytes. Infer the chunk size by querying 1-, 2-, 3-byte inputs and comparing lengths against normal base64.
- **Minecraft world NBT extraction:** A zipped Minecraft world can be solved without launching the game. Use MCA Selector to locate the region/chunk from coordinates, then inspect `r.X.Z.mca` with NBTExplorer; block entities such as chests, signs, furnaces, and books often hold ordered item names or text where first letters, counts, or slots encode the answer.

## Local Learnings Appended 2026-04-24

- **Nuclei scanner oracle challenge:** If a service runs `nuclei -u <url> -t custom-template.yaml` and rewards specific stdout strings, read the template matchers/extractors and host a page that exactly satisfies them. Treat the scanner as an oracle over your controlled HTTP responses, including expected paths, headers, status codes, and body keywords.

## Local Learnings Appended 2026-04-30

- **Case-sensitive pyjail blacklist bypass:** If a Python jail blocks lowercase names like `system` or `import` but evaluates expressions case-sensitively, synthesize names with string methods: `__builtins__.__dict__['__IMPORT__'.lower()]('OS'.lower()).__dict__['SYSTEM'.lower()](cmd)`. If stdout is broken, write the flag to `sys.stderr`.
- **Lua registry sandbox escape:** If a Lua jail nils globals such as `io.open` but stores originals in a helper table, inspect `debug.getregistry()` for those preserved references. Payloads like `debug.getregistry().safe_method.open("flag","r"):read("*a")` can bypass globals-only restrictions.
- **Character-by-character restricted read:** In shells where normal file readers or options are blocked, try `grep -o . flag.txt` to emit one character per line. This can bypass filters that only block bulk output commands or common flags.

## Local Learnings Appended 2026-05-06

- **Special-character bot/agent name as auth bypass:** When a custom AI/chat bot demands a "signature" to talk and the bot's display name contains an unusual unicode/special character, send that exact special character (or the literal name) as input. Signature checks built around `name == expected_name` can match trivially when the user-supplied "name" equals the configured bot identity, bypassing the signature step entirely. Inspect the bot name with `[hex(ord(c)) for c in name]` first.
- **Japanese number-word landmark heights:** Spelled-out Japanese numerals embedded in chat ("roku-hyaku san-juu yon" = 634) frequently encode famous landmark heights/codes (Tokyo Skytree = 634m). When OSINT-bot puzzles return a numeric word, recognize as Japanese 漢数字, convert to a number, and search "<number> + <theme>" landmarks; the resulting place name yields a what3words address (e.g., `watches.caked.land`) for the flag.
- **ERC20 transfer selector decoding:** In blockchain forensics CTFs, calldata starting with `0xa9059cbb` is `transfer(address,uint256)`. Next 32 bytes are the recipient address (right-padded), next 32 bytes are the amount. Common amounts encoded as hex: `0x2b5e3af16b1880000` = 50 ETH, `0x0de0b6b3a7640000` = 1 ETH, `0x8ac7230489e80000` = 10 ETH. Use the recipient as the attacker address and concatenate with other recovered fragments for the flag.
- **Decimal-to-hex-to-ASCII clue chain:** When server logs contain unusual large decimal numbers (`process_9042_anomaly: 26852480951005303`), convert via `hex(N)` then `bytes.fromhex` — the result is often readable ASCII fragments (`5f66306c6c3077` → `_f0ll0w`). Apply to every numeric log field; chained fragments concatenate into the flag suffix. BSON/JSON `meta_integrity` fields with base64 → hex → ASCII follow the same pattern.
- **Hex-encoded address concatenation flag pattern:** Blockchain CTF flags often follow `FLAG{0x<address>_<word1>_<word2>_<word3>}` where each word came from a different log field decoded individually. Collect all decoded fragments first, then assemble with the recovered address as prefix.
- **"Old secret in .backup folder" hint:** When source-code snippets reference legacy/old secret storage (e.g., `keys/.backup/`), this is the JWT `kid` traversal target — see also ctf-web JWT `kid` techniques. Decoded help cookies (`recipe_hint`, `algo_hint` base64) often point to the relevant `/admin-recipe` or `/debug/info` endpoint in the same challenge.

## Local Learnings Appended 2026-05-08

- **Zero-width Unicode hidden text/key carrier:** When text looks normal but has odd spacing, line behavior, or a suspicious byte length, scan for zero-width codepoints such as `U+200B` and `U+200C`. Preserve the original file, count/remove them for visible-text triage, and try a ZWSP/ZWNJ stego decoder before overfitting custom bit grouping; the hidden payload may be a password, Vigenere key, or final flag fragment.

