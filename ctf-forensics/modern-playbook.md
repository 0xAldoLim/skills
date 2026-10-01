# ctf-forensics modern solving playbook

Research window: 2024-01-01 through 2026-10-01. These are concise, independently written source-derived methods. Source review is not a successful local reproduction. Confirm the stated prerequisite cheaply before spending remote queries. Existing references retain older and complementary variants. All instance actions follow ../docs/SCOPE.md.

## Shuffled capture to sparse encrypted disk reconstruction

**Signal / prerequisite:** Negative time deltas accompany ICMP command/reply fragments and an encrypted disk.
**Cheapest useful test:** Inspect timestamp ordering and decompress one identified payload offline.
**Primitive and method:** Reorder only a working copy; reconstruct octal little-endian words with offsets/repeated-line notation, place recovered dd blocks into a sparse image, then validate the LUKS metadata/key provenance.
**Failure / wasted work:** Missing offsets, repeated rows or zero-filled gaps corrupt the image; never execute recovered shell commands.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** high; timestamp sort, offset-aware decoder and sparse block writer.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/ctf-gemastik/penyisihan-2024/blob/b5800ac9f044bd43056b3251fe1b51eb135969e4/forensics/Oddly/writeup/README.md).

## Persistence links registry to ransomware

**Signal / prerequisite:** Run-key artifacts point to batch and PowerShell stages.
**Cheapest useful test:** Resolve referenced paths from the supplied disk/registry data.
**Primitive and method:** Build a timestamped stage graph, statically decode script layers and derive key/IV/encoding before decrypting a copy.
**Failure / wasted work:** A key-looking string without a matching encryption path is not enough; do not run the ransomware.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/ctf-gemastik/penyisihan-2024/blob/b5800ac9f044bd43056b3251fe1b51eb135969e4/forensics/ruze/writeup/README.md).

## TLS keylog reveals covert IP identification encoding

**Signal / prerequisite:** Supplied TLS secrets decrypt traffic containing a Scapy encoder; another flow has unusual IP IDs.
**Cheapest useful test:** Decrypt only the supplied capture and inspect the encoder as text.
**Primitive and method:** Filter the exact covert flow, preserve packet order/retransmission semantics and invert the documented ID transform; validate bytes against protocol structure.
**Failure / wasted work:** Mixing background traffic produces plausible garbage; do not assume every low-entropy header is a channel.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** low; tshark fields plus offline inverse transform.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/osirislab/CSAW-CTF-2024-Quals/blob/f2238204ff78d167f6d977aec8705f19897eb554/forensics/covert/solution/solution.md).

## Split encrypted archive delivered by mail

**Signal / prerequisite:** A capture contains repeated SMTP exchanges and file fragments.
**Cheapest useful test:** List streams and inspect one transfer MIME structure.
**Primitive and method:** Reassemble each mail conversation, decode attachments once, order the numbered pieces and use evidenced passwords offline.
**Failure / wasted work:** Truncated streams, duplicate captures or decoding the concatenation at the wrong layer breaks reconstruction.
**Pivot:** Recheck the prerequisite; switch to the nearest category/reference if it is absent.
**Cost / automation:** medium; offline parser or replay script.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://github.com/hackthebox/cyber-apocalypse-2024/blob/4e59eec7a4919d2a4ae4f5d98ecf8ba153ac464a/forensics/%5BMedium%5D%20Phreaky/README.md).

## Timed GIF frame extraction

**Signal / prerequisite:** A GIF seems stuck despite multiple frames.
**Cheapest useful test:** Inspect frame count and delay metadata.
**Primitive and method:** Extract/coalesce every frame without waiting; preserve disposal/blend behavior.
**Failure / wasted work:** Raw frame rectangles can omit prior pixels.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** low; Pillow ImageSequence or ImageMagick coalescing.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://hong5489.github.io/2024-12-30-wgmy2024/).

## SMB encryption from evidenced NTLMv2 exchange

**Signal / prerequisite:** An encrypted SMB capture includes its NTLMv2 handshake.
**Cheapest useful test:** Associate session ID, NTProofStr and encrypted exported session key.
**Primitive and method:** Only with an evidenced offline credential candidate, derive protocol session keys and decrypt a copy of the capture. Uppercase the username as required; do not arbitrarily uppercase the domain.
**Failure / wasted work:** Handshake/session mismatch, missing key exchange or wrong password prevents decryption.
**Pivot:** Recheck the exact format/runtime; retain competing interpretations.
**Cost / automation:** medium; offline NTLMv2 derivation and tshark/Wireshark keys.
**Verification:** primary-source review; challenge reproduction pending.
**Source:** [writeup or organizer solve](https://oxygen28.github.io/posts/wargamesmy2024/).
