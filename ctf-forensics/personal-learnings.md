# Personal verified challenge learnings

> Execution guard: historical examples are knowledge, not target authorization. Instance-only scope, bounded requests, local isolation and version checks in ../docs/SCOPE.md and ../docs/WORKFLOW.md take precedence. Never execute recovered malware or model/pickle payloads on the host.

Read only sections matching current evidence. The instance boundary in [scope](../docs/SCOPE.md) applies to every historical example. Historical endpoints are evidence, never new authorized targets.

## Local Learnings Appended 2026-04-19

- **Numeric markers can be selectors, not payload:** When a PNG or other stego artifact yields numeric marks, do not assume they are final values. Check whether another artifact provides prose instructions or a thematic key that transforms those numbers into packet indices, offsets, or lookup keys for a second artifact such as a PCAP.
- **Alpha-channel packet selector pipeline:** If hidden alpha values look like packet references but the chosen packets are uninteresting, test a uniform transform first, especially XOR from a textual clue. A short transformed selector list can point directly to the few packets whose payload fragments complete the flag.
- **Channel-difference instruction recovery:** When LSB and bitplane extraction from a normal-looking image are mostly noise, try channel-difference views to surface faint instruction text that redirects the solve path.
- **Log-derived route to structured lookup:** If you have a map/image, movement log, and structured JSON-like room data, test whether the log defines a route through the structured artifact. Per-node values collected along that route may encode the answer more directly than the visible map labels.
- **Reverse the whole extracted hex string:** When a route trace or artifact lookup yields a nearly plausible hex string, test full-string reversal before trying byte swaps or pairwise reversal. Some challenges hide the final message by reversing the entire concatenated hex stream.
- **X11 PutImage frame recovery:** In PCAPs with X11 traffic, filter for `PutImage` requests and inspect `ZPixmap` payloads. Strip the request header bytes, decode the remaining payload as raw RGBA with the advertised width and height, then sort repeated frames by packet or embedded filename order to reconstruct the image sequence.

## Local Learnings Appended 2026-04-23

- **Cloud bucket service-account pivot:** If an exposed bucket contains a GCP service-account JSON key, activate it locally with `gcloud auth activate-service-account --key-file=...`, set the leaked project, then enumerate all accessible buckets with `gcloud storage list` or `gsutil ls`. The flag may sit in a different bucket than the one that leaked the credential.

## Local Learnings Appended 2026-04-24

- **Exfiltrated Firefox profile recovery:** If PCAP malware uploads a `firefox_profiles.zip`, extract HTTP objects first, then look for `key4.db`, `logins.json`, `cookies.sqlite`, and `cert9.db`. Use `firefox_decrypt.py` against the recovered profile directory; saved passwords often hold the next URL, paste password, or flag-adjacent credential.
- **LNK-embedded payload key correction:** For suspicious Windows shortcuts, inspect `Arguments` with `lnkinfo`; PowerShell may XOR the `.lnk` bytes, skip an offset, and write an embedded executable. If the documented XOR key yields no `MZ`/`PE` header, recover the real one by XORing the carved bytes at the skip offset against known PE magic before decompiling the payload.

## Local Learnings Appended 2026-04-28

- **Bitcoin case-amount correlation:** In blockchain forensics tied to a real-world incident, convert the reported fiat payment at the incident date into approximate satoshis, then trace ATM deposits, consolidation transactions, and near-matching outbound amounts. The correct payment may be a slightly smaller BTC output plus change, not the largest peel-chain output.

## Local Learnings Appended 2026-04-30

- **Ethernet trailer exfil after ARP poisoning:** If a PCAP shows duplicate-IP warnings or ARP poisoning, filter the suspicious MAC-to-MAC direction and extract `eth.trailer` with tshark. Covert payload fragments may live after the normal frame payload and reassemble directly into the flag.
- **PKZIP known-plaintext from PE DOS stub:** For encrypted ZIPs containing an EXE, use the predictable DOS stub string `This program cannot be run in DOS mode.\r\r\n` as known plaintext for `bkcrack`. Locate the exact offset with `grep -aob`, recover ZIP keys once, then decrypt unrelated encrypted members such as custom flag blobs.
- **WebSocket PCAP credential triage:** When a capture contains WebSocket traffic, filter on `websocket`, follow messages, and decode base64-looking frames. Failed and successful login attempts can be separated by server responses; the successful frame often carries plaintext credentials or command output after decoding.
- **TLS keylog mismatch check:** If a challenge provides both `sslkeylog.txt` and multiple PCAPs, do not assume the keylog matches the named capture. Load the keylog into Wireshark and test each TLS-heavy capture; decrypted HTTP appearing in one capture is the fastest confirmation.
- **Office macro fallback to raw stream strings:** When `olevba` fails on a DOCX macro project, unzip or binwalk the document and run `strings` directly on `word/vbaProject.bin`. Obfuscated payloads, esolangs, URLs, or base64 layers can survive even when macro parsers report corruption.
- **MFTExplorer for resident MFT contents:** If MFTECmd finds a suspicious filename in an `$MFT` artifact but does not expose content, open the MFT in MFTExplorer or another record-level viewer. Small resident files can be recovered directly from the MFT entry without a full disk image.
- **Android gesture SHA-1 in documents:** In mobile-forensics-themed documents, a lone SHA-1 hash can be an Android gesture lock rather than a generic password hash. Try gesture-cracking tools or lookup scripts before treating it as normal NTLM/SHA1 cracking.

## Local Learnings Appended 2026-04-30

- **DNS fragments ordered by TTL:** If DNS subdomain labels look base32/base64 but decode to junk in packet order, inspect DNS response metadata such as TTL. Sequential TTL values can be the ordering key; sort by TTL, uppercase Base32 labels, decode to bytes, then check for compressed signatures such as gzip.
- **TCP fragment ordering by destination port:** In PCAP puzzles with base64-looking payloads spread across several destination ports, raw packet order may be wrong. Group or sort fragments by destination port first, then packet number within each port, before base64 decoding and repairing the recovered file signature/chunks.
- **OSPF router-ID coordinate ASCII:** OSPF router IDs shaped like `10.x.y.byte` can carry both drawing coordinates and plaintext. Extract `ospf.srcrouter`, sort by the sender/order field, and read the final octet as ASCII while using the middle octets to visualize the path if needed.
- **Spectrogram coordinates drive image trail:** When a WAV spectrogram yields coordinate pairs and a companion image exists, reuse the same coordinates as numeric inputs. A sum such as `sum(x*y)` may define an image offset, and changed pixels between base/challenge images can follow a trail where channel operations such as `R xor B` decode text.
- **Stereo phase-cancellation Morse:** For stereo audio where hints mention opposites or silence, subtract one channel from the other to cancel common audio. Normalize the difference track, listen or plot it for dot/dash bursts, then decode the resulting Morse before applying any hinted classical cipher.
- **Matroska attachment and subtitle layers:** MKV/MP4 containers can hide attached files and subtitle streams rather than pixel/audio stego. Use `ffprobe` to enumerate attachments, extract the embedded media, then inspect subtitle tracks for ordered base64 chunks and decoys.
- **Windows memory UTF-16 string pass:** If ASCII `strings` misses flags in a Windows memory dump, rerun with UTF-16LE extraction such as `strings -a -el -n 6`. Command lines, flags, and archive passwords often survive only in wide strings.
- **7-Zip password from process command line:** For encrypted `.7z` archives with header encryption (`-mhe=on`), search memory for the original `7z.exe a ... -pPASSWORD` command line before cracking. A recovered `-p` argument can unlock the archive directly.
- **Edge history SQLite triage:** On Windows user images, Edge history lives under `AppData/Local/Microsoft/Edge/User Data/Default/History`. Copy the SQLite DB out, query visited URLs, and treat unusual GitHub Pages or local-file URLs as likely staging/flag artifacts.
- **Paired-image diff over metadata:** If a challenge provides or accidentally leaks both an original/base image and a modified image, diff RGB arrays before deep stego tooling. Sort changed pixel coordinates by `(y, x)` and inspect per-channel values at only those pixels; the hidden message may live entirely in sparse modifications.
- **Triangular trail validation:** When spectrogram-derived coordinates produce an offset into an image, validate the changed-pixel path against simple progressions before decoding. A trail such as `y_i = offset + i*(i+1)//2` confirms ordering and prevents reading unrelated changed pixels.
- **Literal channel-operation hints:** Hints like "Red XORs Blue" can mean decode each selected pixel as `chr(R ^ B)` from the modified image, not LSB extraction or image-difference bytes. Apply the named channel operation at validated landing points after the path is proven.

## Local Learnings Appended 2026-05-06

- **Disguised-extension audio spectrogram:** A `.dat`/`.tmp`/`.bin` artifact in a `temp/`-style folder may be a renamed WAV. Run `file` first; if it reports RIFF/WAVE, render a spectrogram (`sox file -n spectrogram` or Audacity) before listening — flags often live in the visual band, not the audio.
- **Carve deleted ZIP via PK magic + `dd`:** When `.bash_history` shows a recent `zip` followed by `rm`, the archive likely still lives in unallocated blocks. Use `grep -obaP "\x50\x4b\x03\x04" image.dd` to find the local-file-header offset, then `dd if=image.dd bs=1 skip=$OFFSET count=<size> of=carved.zip`. Estimate `count` from observed footers (`PK\x05\x06`) or err on the long side and let `unzip` ignore trailing junk.
- **`.bash_history` password-via-cat pattern:** Recipes like `zip -P "$(cat ~/.cache/.session_key)" backup.zip keep.jpg` mean the password is the file at the cat-target. Read that file (often a hidden dotfile under `~/.cache` or `~/.config`) to recover the shell-substituted secret.
- **Reused-password ZIP+steghide chain:** When a recovered ZIP password unlocks a JPEG inside, also try the SAME password against `steghide extract -sf img.jpg -p <pwd>`. Lazy challenge authors reuse the credential across both stages; the extracted file may itself be base64 wrapping the flag.
- **Windows MiniDump (`MDMP` magic) memory triage:** A `.DMP` (or any extension) file whose `file` reports "MS Windows Minidump" is raw process memory. Skip executable-style analysis — go straight to `strings -a file.DMP | grep -Ei "flag|FindITCTF|http|upload|checksum|aes|gcm|key"` to surface URLs, file paths, and crypto API references that pinpoint the stealer's behavior.
- **Go-binary AES-GCM fingerprints in dumps:** Strings like `NewGCM`, `*gcm.GCM`, `*aes.Block`, `crypto/aes.(*aesCipher)` indicate AES-GCM in a Go process. The AES key sits as a 32-byte (AES-256) or 16-byte (AES-128) high-entropy blob in memory near the related strings; carve candidates from offsets within ~64KB of those references.
- **AES-GCM blob arithmetic for flag identification:** AES-GCM ciphertext format is `12-byte nonce || ciphertext || 16-byte tag`. For a request body of length `L`, plaintext length is `L - 28`. When two encrypted POSTs exist (e.g., `/upload` 2.1MB and `/checksum` 72B), the small one with `L - 28 ≈ flag length (~44)` is the target — decrypt the small blob first.
- **Carve HTTP body from memory dump:** Locate `POST /endpoint HTTP/1.1` in the dump, find the next `\r\n\r\n` to skip headers, then read the next `Content-Length` bytes as the body. Useful for extracting C2 payloads, encrypted blobs, or uploaded files from crash dumps.
- **Windows `dumpfiles` memory image hash:** For a malicious EXE that "remains in memory", do not stop at the VT/on-disk SHA256 or `malfind` VAD hash. Run `windows.filescan` to get the file object, then `windows.dumpfiles` and hash every emitted stream. Volatility commonly emits `DataSectionObject` (cached file/data bytes) and `ImageSectionObject` (the mapped in-memory executable image); CTF wording about a binary remaining in memory may expect the `ImageSectionObject.*.img` SHA256 even when the `DataSectionObject.*.dat` hash matches the public malware sample.

## Local Learnings Appended 2026-05-19

- **SQLite WAL plus thumbnail-cache AES-GCM:** In mobile app snapshots, preserve SQLite `-wal` sidecars before opening the database. Deleted WAL rows may contain decoy flags plus split key fragments, while thumbnail-cache images may carry LSB JSON with `nonce`, `tag`, `ciphertext`, and `aad`. If a clue provides a thumbnail salt, test derivations such as `sha256(K1 || K2 || "thumb-salt:<salt>")` and decrypt with AES-GCM using the embedded AAD.

