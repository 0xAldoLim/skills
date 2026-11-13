#!/usr/bin/env python3
"""Durable CTF evidence, hypotheses and verification ledger.

The ledger keeps observations, facts, hypotheses, candidates and verification
separate so a plausible flag or a tool's "verified" line cannot silently become
success. It writes solve/evidence.jsonl plus compact Markdown views.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TRUST_LEVELS = {"operator", "local", "untrusted", "external"}
ORIGINS = {"static", "runtime", "derived", "oracle", "claim"}
METHODS = {"checker", "derivation", "service", "commitment", "platform"}
REJECTED_METHODS = {"claim", "format", "regex", "scan", "readme", "model", "tool", "guess", "assertion"}
MAX_ACTIVE = 3


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_event(directory: Path, event: dict) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    event = {"time": now(), **event}
    with (directory / "evidence.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    sync_markdown(directory)
    return event


def load_events(directory: Path) -> list[dict]:
    path = directory / "evidence.jsonl"
    if not path.is_file():
        return []
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid evidence line {number}: {error}") from error
        if not isinstance(value, dict) or "event" not in value:
            raise ValueError(f"evidence line {number} is not an event object")
        events.append(value)
    return events


def derive(events: list[dict]) -> dict:
    state = {
        "target": None,
        "mode": None,
        "observations": [],
        "facts": [],
        "hypotheses": {},
        "candidates": {},
        "verifications": [],
    }
    for event in events:
        kind = event.get("event")
        if kind == "init":
            state["target"] = event.get("target")
            state["mode"] = event.get("mode")
        elif kind == "observation":
            state["observations"].append(event)
        elif kind == "fact":
            state["facts"].append(event)
        elif kind == "hypothesis":
            state["hypotheses"][event["id"]] = {**event, "status": "active"}
        elif kind == "hypothesis_status":
            item = state["hypotheses"].get(event.get("hypothesis") or event.get("id"))
            if item:
                item["status"] = event.get("status", item["status"])
                item["reason"] = event.get("reason", "")
        elif kind == "candidate":
            state["candidates"][event["id"]] = {**event, "verified": False, "verifications": []}
        elif kind == "verification":
            state["verifications"].append(event)
            candidate = state["candidates"].get(event.get("candidate"))
            if candidate:
                candidate["verifications"].append(event)
                method = str(event.get("method", "")).lower()
                result = str(event.get("result", "")).strip()
                independent = method in METHODS and len(result) >= 3
                if method == "platform" and not event.get("operator_authorized"):
                    independent = False
                if candidate.get("origin") == "claim":
                    independent = False
                candidate["verified"] = bool(candidate["verifications"]) and independent
    return state


def next_id(events: list[dict], prefix: str) -> str:
    count = sum(1 for event in events if event.get("id", "").startswith(prefix) and event.get("id", "")[1:].isdigit())
    return f"{prefix}{count + 1}"


def sync_markdown(directory: Path) -> None:
    state = derive(load_events(directory))
    facts = state["facts"]
    candidates = list(state["candidates"].values())
    verified = [item for item in candidates if item.get("verified")]
    lines = [
        "# Solve state",
        "",
        f"Target: {state['target'] or 'local artifacts only'}",
        f"Mode: {state['mode'] or 'FAST'}",
        f"Updated: {now()}",
        "",
        "## Proven facts",
        "",
    ]
    lines.extend(f"- {item.get('text', '')} {('[' + ','.join(item.get('support', [])) + ']') if item.get('support') else ''}".rstrip() for item in facts)
    if not facts:
        lines.append("- (none recorded)")
    lines.extend(["", "## Candidates", ""])
    if candidates:
        for item in candidates:
            status = "VERIFIED" if item.get("verified") else "unverified"
            lines.append(f"- {item['id']}: `{item.get('value', '')}` origin={item.get('origin')} {status}")
    else:
        lines.append("- (none recorded)")
    if verified:
        lines.extend(["", f"Verified flag: `{verified[0].get('value', '')}`"])
    lines.extend(["", "## Next test", "", "- See HYPOTHESES.md; do not repeat an unchanged failed call.", ""])
    (directory / "STATE.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")

    hyp = ["# Active hypotheses", "", "Keep at most three. Retire one before adding a fourth.", "",
           "| ID | Hypothesis | Evidence | Cheapest discriminator | Predicted observation | Cost | Pivot if | Status |",
           "|---|---|---|---|---|---|---|---|"]
    for item in state["hypotheses"].values():
        if item.get("status") != "active":
            continue
        hyp.append(
            "| {id} | {text} | {evidence} | {test} | {predict} | {cost} | {pivot} | active |".format(
                id=item.get("id", ""), text=item.get("text", ""), evidence=item.get("evidence", ""),
                test=item.get("test", ""), predict=item.get("predict", ""), cost=item.get("cost", "medium"),
                pivot=item.get("pivot", ""),
            )
        )
    hyp.extend(["", "## Retired", "", "| ID | Reason |", "|---|---|"])
    for item in state["hypotheses"].values():
        if item.get("status") == "retired":
            hyp.append(f"| {item.get('id')} | {item.get('reason', '')} |")
    (directory / "HYPOTHESES.md").write_text("\n".join(hyp) + "\n", encoding="utf-8", newline="\n")


def command_init(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    if events:
        raise ValueError("evidence ledger already exists; use status or a new directory")
    event = append_event(args.dir, {"event": "init", "target": args.target, "mode": args.mode})
    return {"ok": True, "event": event, "directory": str(args.dir)}


def command_observe(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    text = args.text
    if args.file:
        raw = Path(args.file).read_bytes()
        text = raw.decode("utf-8", errors="replace")[: args.max_chars]
    if not text:
        raise ValueError("observation text is empty")
    text = text[: args.max_chars]
    event = append_event(args.dir, {
        "event": "observation", "id": next_id(events, "O"),
        "source": args.source, "trust": args.trust,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text": text,
    })
    return {"ok": True, "event": event}


def command_fact(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    event = append_event(args.dir, {
        "event": "fact", "id": next_id(events, "F"), "text": args.text,
        "support": args.support or [],
    })
    return {"ok": True, "event": event}


def command_hypothesis(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    active = [item for item in derive(events)["hypotheses"].values() if item.get("status") == "active"]
    if len(active) >= MAX_ACTIVE:
        raise ValueError("three active hypotheses already exist; retire one first")
    event = append_event(args.dir, {
        "event": "hypothesis", "id": next_id(events, "H"), "text": args.text,
        "evidence": args.evidence or "", "test": args.test or "",
        "predict": args.predict or "", "cost": args.cost, "pivot": args.pivot or "",
    })
    return {"ok": True, "event": event}


def command_retire(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    if args.id not in derive(events)["hypotheses"]:
        raise ValueError(f"unknown hypothesis {args.id}")
    event = append_event(args.dir, {
        "event": "hypothesis_status", "hypothesis": args.id, "status": "retired", "reason": args.reason,
    })
    return {"ok": True, "event": event}


def command_candidate(args: argparse.Namespace) -> dict:
    events = load_events(args.dir)
    event = append_event(args.dir, {
        "event": "candidate", "id": next_id(events, "C"), "value": args.value,
        "origin": args.origin, "support": args.support or [], "note": args.note or "",
    })
    return {"ok": True, "event": event}


def command_verify(args: argparse.Namespace) -> dict:
    method = args.method.lower()
    if method in REJECTED_METHODS or method not in METHODS:
        raise ValueError(f"method {method!r} is not independent verification")
    if method == "platform" and not args.operator_authorized:
        raise ValueError("platform submission requires --operator-authorized")
    if len((args.result or "").strip()) < 3:
        raise ValueError("verification requires an observed result, not a claim")
    events = load_events(args.dir)
    state = derive(events)
    candidate = state["candidates"].get(args.candidate)
    if not candidate:
        raise ValueError(f"unknown candidate {args.candidate}")
    if candidate.get("origin") == "claim":
        raise ValueError("a claimed candidate cannot be verified; recover an independent value")
    event = append_event(args.dir, {
        "event": "verification", "id": next_id(events, "V"), "candidate": args.candidate,
        "method": method, "result": args.result.strip(), "command": args.command or "",
        "artifact": args.artifact or "",
    })
    return {"ok": True, "event": event, "candidate": candidate.get("value")}


def command_status(args: argparse.Namespace) -> dict:
    state = derive(load_events(args.dir))
    active = [item for item in state["hypotheses"].values() if item.get("status") == "active"]
    candidates = []
    for item in state["candidates"].values():
        candidates.append({
            "id": item["id"], "value": item.get("value"), "origin": item.get("origin"),
            "verified": item.get("verified"), "support": item.get("support", []),
            "methods": [entry.get("method") for entry in item.get("verifications", [])],
        })
    verified = [item for item in candidates if item["verified"]]
    warnings = []
    if len(active) > MAX_ACTIVE:
        warnings.append("more than three active hypotheses")
    if any(item["origin"] == "claim" for item in candidates):
        warnings.append("claim-origin candidate present; it cannot be verified")
    return {
        "target": state["target"], "mode": state["mode"], "facts": state["facts"],
        "active_hypotheses": active, "candidates": candidates,
        "verified_flag": verified[0]["value"] if verified else None,
        "warnings": warnings, "events": len(load_events(args.dir)),
    }


def command_check(args: argparse.Namespace) -> dict:
    errors = []
    events = load_events(args.dir)
    ids = set()
    for event in events:
        identifier = event.get("id")
        if identifier:
            if identifier in ids:
                errors.append(f"duplicate id {identifier}")
            ids.add(identifier)
    state = derive(events)
    active = [item for item in state["hypotheses"].values() if item.get("status") == "active"]
    if len(active) > MAX_ACTIVE:
        errors.append("more than three active hypotheses")
    for candidate in state["candidates"].values():
        if candidate.get("origin") not in ORIGINS:
            errors.append(f"candidate {candidate.get('id')} has invalid origin")
        if candidate.get("verified") and not candidate.get("support"):
            errors.append(f"verified candidate {candidate.get('id')} has no supporting evidence")
    for event in state["verifications"]:
        method = str(event.get("method", "")).lower()
        if method not in METHODS or len(str(event.get("result", "")).strip()) < 3:
            errors.append(f"verification {event.get('id')} uses an invalid or empty method")
        if method == "platform" and not event.get("operator_authorized"):
            errors.append(f"verification {event.get('id')} claims platform acceptance without operator authorization")
    return {"ok": not errors, "errors": errors, "events": len(events)}


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dir", type=Path, default=Path("solve"), help="state directory (default: solve)")
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", parents=[common])
    init.add_argument("--target")
    init.add_argument("--mode", choices=["FAST", "EXPERT"], default="FAST")
    init.set_defaults(func=command_init)

    observe = sub.add_parser("observe", parents=[common])
    observe.add_argument("--source", required=True)
    observe.add_argument("--text")
    observe.add_argument("--file")
    observe.add_argument("--trust", choices=sorted(TRUST_LEVELS), default="untrusted")
    observe.add_argument("--max-chars", type=int, default=4000)
    observe.set_defaults(func=command_observe)

    fact = sub.add_parser("fact", parents=[common])
    fact.add_argument("--text", required=True)
    fact.add_argument("--support", action="append", default=[])
    fact.set_defaults(func=command_fact)

    hypothesis = sub.add_parser("hypothesis", parents=[common])
    hypothesis.add_argument("--text", required=True)
    hypothesis.add_argument("--evidence")
    hypothesis.add_argument("--test")
    hypothesis.add_argument("--predict")
    hypothesis.add_argument("--cost", choices=["low", "medium", "high"], default="medium")
    hypothesis.add_argument("--pivot")
    hypothesis.set_defaults(func=command_hypothesis)

    retire = sub.add_parser("retire", parents=[common])
    retire.add_argument("--id", required=True)
    retire.add_argument("--reason", required=True)
    retire.set_defaults(func=command_retire)

    candidate = sub.add_parser("candidate", parents=[common])
    candidate.add_argument("--value", required=True)
    candidate.add_argument("--origin", choices=sorted(ORIGINS), required=True)
    candidate.add_argument("--support", action="append", default=[])
    candidate.add_argument("--note")
    candidate.set_defaults(func=command_candidate)

    verify = sub.add_parser("verify", parents=[common])
    verify.add_argument("--candidate", required=True)
    verify.add_argument("--method", required=True)
    verify.add_argument("--result", required=True)
    verify.add_argument("--command")
    verify.add_argument("--artifact")
    verify.add_argument("--operator-authorized", action="store_true")
    verify.set_defaults(func=command_verify)

    status = sub.add_parser("status", parents=[common])
    status.set_defaults(func=command_status)

    check = sub.add_parser("check", parents=[common])
    check.set_defaults(func=command_check)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.func(args)
    except (ValueError, OSError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
