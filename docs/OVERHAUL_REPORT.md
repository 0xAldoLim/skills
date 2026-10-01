# CTF skills repository overhaul

Completed implementation from personal commit `d95fd4433d0656f5de29b04a64e28801c01f127c`. Commit and push were explicitly requested after the local overhaul was validated. Existing installed skills were not modified.

## 1. Architecture changes

Nine operational roots and the dispatcher now inventory locally, establish scope/health, test cheap evidence-backed hypotheses, retrieve targeted references, verify a flag and capture qualified knowledge. Persistent STATE/HYPOTHESES/findings and adaptive modes avoid restarting hard solves.

## 2. Upstream synchronization

Fetched upstream main at `c332c7be1b27cb64639a20124ac55ba916adef92` on 2026-10-01. Recorded 42 imports of sections/references and reviewed 102 overlapping changes. Personal additions remain authoritative. [Complete decisions](../knowledge/migration/upstream-decisions.json) retain source and destination.

## 3. Research

Reviewed 54 contributing CTF technical source URLs: 50 technical writeup URLs and 4 solver-source URLs. Produced 56 cards across 20 competitions and all nine categories. Reviewed 12 separate primary documentation/foundation sources. Unique regional URLs: Indonesia 6; Malaysia 4. English, Indonesian and Malay searches were used. Downloads, catalogs and pointer pages are counted separately; notes are source-reviewed, not end-to-end reproduced. [Research ledger](../knowledge/research-sources.json).

| Category | New cards |
|---|---:|
| ctf-ai-ml | 5 |
| ctf-crypto | 7 |
| ctf-forensics | 6 |
| ctf-malware | 5 |
| ctf-misc | 6 |
| ctf-osint | 6 |
| ctf-pwn | 6 |
| ctf-reverse | 8 |
| ctf-web | 7 |

Competitions: 0CTF 2024, CSAW CTF 2024 Qualifiers, DEF CON CTF 2025 Qualifiers, DownUnderCTF 2024, DownUnderCTF 2025, GEMASTIK 2024 Qualifiers, Google CTF 2024 Quals, HITCON CTF 2024, HTB Cyber Apocalypse 2024, HTB Cyber Apocalypse 2025, Hack.lu CTF 2024, IDSECCONF 2025 Finals, Insomni'hack 2025, LA CTF 2026, PlaidCTF 2025, SECCON 13 Online CTF (2024), SekaiCTF 2025, Siber Siaga CTF 2025 Finals, UIUCTF 2024, Wargames.MY 2024.

## 4. Knowledge improvements

Added prerequisite/evidence variants including shared-polynomial MPC, tensor/tokenizer IDs, sparse packet/disk reconstruction, GIF timing, layered session crypto, Go metadata and ABI-specific integer wrap. 43 correction entries address faulty math, allocator/CET assumptions, AEAD serialization, unsafe model loading and malformed code. [Correction ledger](../knowledge/migration/corrections.json).

## 5. Personal knowledge preservation

All 193 original tracked files and 238 root sections are accounted for: 191 relocated, 43 superseded workflow sections and four corrected root sections. All 19 personal sections remain verbatim. Existing LEARNED and accepted records remain; 142 reference prefixes are protected. [Section map](../knowledge/migration/section-map.json), [file map](../knowledge/migration/file-map.json), and inactive baseline archive provide recovery. No unexplained removal.

## 6. Token efficiency

Short entrypoints, nine symptom indexes, bounded section lookup and reusable helpers reduce repeated context and code. Root-size measurements below use characters, not billing tokens.

| Entry point | Original characters | Current characters | Reduction |
|---|---:|---:|---:|
| ctf-ai-ml | 7449 | 5458 | 26.7% |
| ctf-crypto | 41415 | 5109 | 87.7% |
| ctf-forensics | 50932 | 4803 | 90.6% |
| ctf-malware | 8804 | 4687 | 46.8% |
| ctf-misc | 32722 | 4915 | 85.0% |
| ctf-osint | 10049 | 4691 | 53.3% |
| ctf-pwn | 20207 | 4947 | 75.5% |
| ctf-reverse | 16727 | 4789 | 71.4% |
| ctf-web | 15012 | 4940 | 67.1% |
| ctf-writeup | 6307 | 1735 | 72.5% |
| solve-challenge | 13430 | 5052 | 62.4% |

## 7. Kali tooling

Installer supports core plus nine category tiers and an explicit heavy tier, isolated Python venv, dry-run/verify/missing-only, and actual dpkg/import checks. Skill installation uses complete-directory symlinks or standalone copies, conflict preflight and sibling backups. Kali 2026.3 needed C/C++ compilers, CMake and pkg-config for Unicorn on Python 3.14; those prerequisites now belong to pwn/reverse tiers. Sage had no apt candidate, so plans report an actionable fallback and accept an existing Sage environment. Heavy stacks were not installed.

```json
{
  "platform": "Linux-6.18.40.1-microsoft-standard-WSL2-x86_64-with-glibc2.43",
  "python": "3.14.7",
  "os_release": "PRETTY_NAME=\"Kali GNU/Linux Rolling\"\nNAME=\"Kali GNU/Linux\"\nVERSION_ID=\"2026.3\"\nVERSION=\"2026.3\"\nVERSION_CODENAME=kali-rolling\nID=kali\nID_LIKE=debian\nHOME_URL=\"https://www.kali.org/\"\nSUPPORT_URL=\"https://forums.kali.org/\"\nBUG_REPORT_URL=\"https://bugs.kali.org/\"\nANSI_COLOR=\"1;31\"\n",
  "container_image": "kalilinux/kali-rolling@sha256:d1d7e581ed60b0bbf9cb8a4bc853526355978f3b943d3a1d7dc7ce209e4231b6"
}
```

## 8. Challenge-instance scope

Every category and the dispatcher allow justified tests of the supplied instance and forbid competition platform/shared infrastructure targeting. Recovered addresses or secrets never add authorization; intended escapes stop at ambiguous shared boundaries.

## 9. Expired-instance handling

Baseline plus at most two confirmation probes; repeated expiry/proxy/connectivity evidence requests refresh. A single 404/500 or silent TCP remains ambiguous. State and solver survive refresh. Local fixtures exercise verified TLS behavior, redirect refusal and bounded deadlines.

## 10. Automatic learning

Strong verified, understood, reproducible and useful novel methods or material prerequisite variants promote automatically. Concept/body comparison replaces title-only suppression; numbers and encoded bytes retain meaning. Exclusive locking/rollback prevents partial promotions. Secrets, flags, ephemeral targets and unverified guesses are excluded.

## 11. Validation

Windows current results: `{"tests": 97, "failures": 0, "errors": 0, "skipped": 4, "passed": 93, "status": "passed", "result_file": "windows-junit.xml"}`. Kali current results: `{"tests": 97, "failures": 0, "errors": 0, "skipped": 0, "passed": 97, "status": "passed", "result_file": "kali-junit.xml"}`. [Windows JUnit](../knowledge/validation/windows-junit.xml), [Kali JUnit](../knowledge/validation/kali-junit.xml), [core readiness](../knowledge/validation/kali-core-readiness.json), [package versions](../knowledge/validation/kali-package-versions.json). Snippet audit: 1,075 Python fences parse, 11 Sage fences require Sage, zero syntax errors. Contextual templates and historical exploits are not claimed as fully executed. Integrity tampering, archive guards, learning transactions, schema, health fixtures, known-answer crypto and Linux pwntools receive targeted tests. GitHub Actions is configured for Ubuntu Python 3.11/3.12 and was not run remotely.

## 12. Files changed

280 changed/added files, listed with status in the [machine report](../knowledge/overhaul-report.json). Original source remains recoverable; significant modifications have migration/correction reasons.

## 13. Remaining meaningful gaps

- DEF CON finals, in-window TCTF, technically valuable picoCTF and DiceCTF need deeper selected source review; catalog/pointer coverage was not promoted as knowledge.
- Malaysia contributions are primarily English with Malay-context sources; search used Malay but fully Malay technical writeups remain underrepresented.
- Independent reproduction of the 56 historical technique cards is still needed before claiming each exploit works on another runtime.
- Heavy Sage/GNU Radio/GPU/architecture/kernel stacks and all-category apt availability require focused validation on the actual user setup.
- Novelty scoring is a conservative explicit feature comparison, not a trained semantic embedding guarantee.
- Historical long references remain substantial and context dependent; targeted retrieval is improved, while full technical correctness of every legacy snippet cannot be claimed.
