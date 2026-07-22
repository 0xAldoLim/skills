#!/usr/bin/env python3
"""Evidence-first CTF category classifier for prompt generation and tests."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SIGNALS: dict[str, tuple[str, ...]] = {
    "ctf-forensics": ("pcap", "pcapng", "memory dump", "disk image", "evtx", "volatility", "steganography", "spectrogram", "packet timing", "deleted file"),
    "ctf-web": ("http", "https", "next.js", "javascript chunk", "sql injection", "xss", "ssti", "ssrf", "jwt", "cookie", "graphql", "template"),
    "ctf-pwn": ("buffer overflow", "format string", "heap", "rop", "shellcode", "ret2libc", "crash", "remote service", "seccomp"),
    "ctf-crypto": ("rsa", "aes", "ecc", "cipher", "encrypt", "modulus", "lattice", "lwe", "nonce", "signature", "prng"),
    "ctf-reverse": ("elf", "binary", "apk", "wasm", "firmware", "bytecode", "custom vm", "obfuscated", "decompile", "disassemble"),
    "ctf-osint": ("identify landmark", "geolocate", "social media", "username", "wayback", "whois", "public records", "reverse image"),
    "ctf-malware": ("malware", "c2", "beacon", "ransomware", "process injection", "packed pe", "yara", "trojan"),
    "ctf-ai-ml": ("machine learning", "neural network", "model extraction", "adversarial example", "prompt injection", "lora"),
    "ctf-misc": ("pyjail", "bash jail", "esolang", "unicode puzzle", "qr puzzle", "rf", "sdr", "logic puzzle", "restricted shell"),
}

EXTENSION_SIGNALS = {
    ".pcap": "ctf-forensics", ".pcapng": "ctf-forensics", ".evtx": "ctf-forensics",
    ".raw": "ctf-forensics", ".e01": "ctf-forensics", ".dd": "ctf-forensics",
    ".apk": "ctf-reverse", ".wasm": "ctf-reverse", ".pyc": "ctf-reverse",
    ".elf": "ctf-reverse", ".so": "ctf-reverse", ".dll": "ctf-reverse", ".exe": "ctf-reverse",
    ".sage": "ctf-crypto", ".pcap.gz": "ctf-forensics",
    ".html": "ctf-web", ".php": "ctf-web", ".js": "ctf-web",
}


def collect_facts(description: str, workspace: Path | None = None, remote: str | None = None) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    if workspace and workspace.exists():
        for path in sorted(workspace.iterdir()):
            if not path.is_file():
                continue
            suffix = "".join(path.suffixes[-2:]).lower() if len(path.suffixes) > 1 else path.suffix.lower()
            files.append({"name": path.name, "suffix": suffix, "size": path.stat().st_size})
    flag_match = re.search(r"(?:flag format|format)\s*[:=]\s*([^\n]+)", description, re.I)
    title_match = re.search(r"(?:title|challenge)\s*[:=]\s*([^\n]+)", description, re.I)
    return {
        "title": title_match.group(1).strip() if title_match else None,
        "description": description.strip(),
        "flag_format": flag_match.group(1).strip() if flag_match else None,
        "files": files,
        "remote_target": remote,
    }


def classify(facts: dict[str, Any]) -> dict[str, Any]:
    text = " ".join([facts.get("description", ""), facts.get("remote_target") or "", " ".join(f["name"] for f in facts.get("files", []))]).lower()
    scores = {category: 0 for category in SIGNALS}
    evidence: dict[str, list[str]] = {category: [] for category in SIGNALS}
    for category, terms in SIGNALS.items():
        for term in terms:
            if term in text:
                scores[category] += 2
                evidence[category].append(f"text signal: {term}")
    for file in facts.get("files", []):
        suffix = file["suffix"]
        category = EXTENSION_SIGNALS.get(suffix) or EXTENSION_SIGNALS.get(Path(file["name"]).suffix.lower())
        if category:
            scores[category] += 3
            evidence[category].append(f"artifact: {file['name']}")
    has_native = any(Path(f["name"]).suffix.lower() in {".elf", ".so", ".exe", ".dll"} or not Path(f["name"]).suffix for f in facts.get("files", []))
    if has_native and facts.get("remote_target"):
        scores["ctf-pwn"] += 4
        evidence["ctf-pwn"].append("native artifact plus remote target")
    if has_native and any(term in text for term in ("custom cipher", "crypto routine", "modular arithmetic")):
        scores["ctf-reverse"] += 3
        scores["ctf-crypto"] += 2
        evidence["ctf-reverse"].append("cryptographic implementation must be reversed")
        evidence["ctf-crypto"].append("secondary cryptanalysis dependency")
    ranked = sorted(scores, key=lambda category: (-scores[category], category))
    primary = ranked[0] if scores[ranked[0]] else "solve-challenge"
    secondaries = [category for category in ranked[1:] if scores[category] and scores[category] >= max(2, scores[ranked[0]] - 4)][:2]
    top = scores[ranked[0]]
    confidence = "high" if top >= 6 and (len(ranked) < 2 or top - scores[ranked[1]] >= 2) else "medium" if top >= 3 else "low"
    return {
        "primary_category": primary,
        "secondary_categories": secondaries,
        "confidence": confidence,
        "evidence": evidence.get(primary, []),
        "scores": {key: value for key, value in scores.items() if value},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--description", required=True)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--remote")
    args = parser.parse_args()
    facts = collect_facts(args.description, args.workspace, args.remote)
    print(json.dumps({"facts": facts, "classification": classify(facts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
