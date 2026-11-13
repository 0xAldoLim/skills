#!/usr/bin/env python3
"""Choose FAST/standard/EXPERT and the first cheap checks from challenge facts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from classify_challenge import classify, collect_facts
from scan_untrusted import scan_text

EXPERT_TERMS = {
    "kernel", "hypervisor", "custom vm", "virtual machine", "custom bytecode",
    "obfuscated", "packed", "firmware", "fpga", "bitstream", "heap", "allocator",
    "use after free", "uaf", "race condition", "multi-stage", "multi stage",
    "zero solve", "no solve", "zero-solve", "hard", "insane", "emulation",
    "symbolic execution", "side channel", "side-channel", "ebpf", "jit",
    "sandbox escape", "vm escape", "trusted execution", "tee", "hypervisor escape",
    "invented language", "custom compression", "unknown cipher", "custom cipher",
    "lattice", "isogeny", "post-quantum", "pqc", "ml-kem", "kyber",
}

FIRST_CHECKS = {
    "ctf-web": ["Map one baseline route/status/auth state", "Trace one source sink or reflected input", "Capture one cookie/session/role assumption"],
    "ctf-pwn": ["Record checksec, interpreter, libc/loader and input path", "Read source/imports for one corruption primitive", "Reproduce one local crash or leak with the supplied runtime"],
    "ctf-crypto": ["Parse exact parameters, encodings and direction", "Test one invariant on a supplied sample", "Establish oracle query/error/timing baseline"],
    "ctf-reverse": ["Identify format, architecture and runtime", "Locate strings/imports and the success/check site", "Trace one short input through the decisive routine"],
    "ctf-forensics": ["Hash and identify the artifact/container", "Extract one structural layer (protocol, filesystem, stream)", "Recover one artifact and verify its hash/round-trip"],
    "ctf-osint": ["Extract metadata/OCR/text clues", "Run one reverse-image/map/archive check", "Corroborate one clue with an independent source"],
    "ctf-malware": ["Hash, identify format and imports", "Decode one stage or config string offline", "Emulate one decisive behavior in isolation"],
    "ctf-ai-ml": ["Inspect container/config/tensor metadata", "Check tokenizer, preprocessing and scoring boundary", "Run one tiny forward pass or bounded transcript"],
    "ctf-misc": ["Identify magic, alphabet and grammar", "Collect two input/output pairs", "Solve or trace one tiny instance"],
    "solve-challenge": ["Inventory files, magic, sizes and hashes", "Classify from evidence and choose one primary skill", "Run the cheapest decisive check"],
}


def plan(facts: dict, *, stuck: bool = False, failed_attempts: int = 0) -> dict:
    classification = classify(facts)
    text = facts.get("description", "").lower()
    triggers = [term for term in EXPERT_TERMS
                if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text)]
    reasons = []
    if stuck:
        reasons.append("operator marked the investigation stuck")
    if failed_attempts >= 2:
        reasons.append(f"{failed_attempts} changed attempts produced no decisive evidence")
    if triggers:
        reasons.append("expert signals: " + ", ".join(sorted(triggers)[:5]))
    if reasons:
        mode = "expert"
    elif classification["confidence"] in {"high", "medium"} and classification["primary_category"] != "solve-challenge":
        mode = "fast"
        reasons.append("clear category with a short expected path")
    else:
        mode = "standard"
        reasons.append("category or primitive needs one more cheap discriminator")
    findings = scan_text(facts.get("description", ""), "<description>")
    return {
        "mode": mode,
        "primary_category": classification["primary_category"],
        "secondary_categories": classification["secondary_categories"],
        "confidence": classification["confidence"],
        "reasons": reasons,
        "first_checks": FIRST_CHECKS.get(classification["primary_category"], FIRST_CHECKS["solve-challenge"]),
        "stop_conditions": [
            "two changed tests with no new discriminating evidence",
            "the branch exceeds its request/query/time budget",
            "the next target leaves the operator-assigned scope",
        ],
        "adversarial_findings": [item for item in findings if item["kind"] != "flag_candidate"],
        "evidence": classification["evidence"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--description", required=True)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--remote")
    parser.add_argument("--stuck", action="store_true")
    parser.add_argument("--failed-attempts", type=int, default=0)
    args = parser.parse_args()
    if not 0 <= args.failed_attempts <= 100:
        parser.error("failed attempts must be 0..100")
    facts = collect_facts(args.description, args.workspace, args.remote)
    print(json.dumps({"facts": facts, "plan": plan(facts, stuck=args.stuck, failed_attempts=args.failed_attempts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
