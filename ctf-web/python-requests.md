# Scoped HTTP experiments and payload processing

Start with a reproducible request to the assigned origin and record status, response fingerprint, parser behavior and authentication state. Read [scope](../docs/SCOPE.md) and [instance health](../docs/INSTANCE_HEALTH.md) first. A redirect, recovered URL or credential never extends the supplied target set. Use verified TLS; if a challenge supplies a private CA, configure that CA instead of disabling checks.

## Bounded request queue

The local helper uses two workers and two requests/second by default, caps requests, queues one small batch at a time and stops on repeated proxy/transport failures or 429. It validates every rendered URL against the exact supplied scheme/host/port and follows no redirects. Treat status/body-hash differences as leads; preserve a baseline and verify the changed primitive with a single replay. Large downloaded wordlists are not the default: derive a small candidate set from source/routes and current evidence.

```bash
python3 "$SKILL_DIR/scripts/async_fuzz.py" --scope solve/scope.json \
  --url 'https://target.example/search?q=FUZZ' --wordlist solve/candidates.txt \
  --max-requests 40 --workers 2 --rate 2 --timeout 3 --dry-run
```

Omit --dry-run only after inspecting that plan. Any increase in rate/workers must be justified by the assigned instance's capacity and query budget; zero solves means deeper analysis, not more traffic. The helper returns metadata rather than a universal exploitation verdict.

## Processing order and byte preservation

`--processing` accepts ordered JSON operations: prefix, suffix, regex replace, substring(start,length), case(upper/lower/title), encode(url/html/base64/hex), decode(url/base64), hash(available hashlib algorithm), and skip(regex). Transformation order changes semantics. Inspect actual bytes locally before spending queries. URL encoding occurs once after processing; use --raw-payload only when the candidate already contains the intended percent encoding. Every raw candidate is still origin-checked, and FUZZ is permitted only in the path/query.

```bash
python3 "$SKILL_DIR/scripts/async_fuzz.py" --scope solve/scope.json \
  --url 'https://target.example/item/FUZZ' --wordlist solve/candidates.txt \
  --processing '[["prefix","known-"],["case","lower"]]' --dry-run
```

For POST/JSON, authentication, multiple insertion points or binary bodies, build a small custom replay from the known baseline. Set a request count/rate/deadline, verify the final URL before every request, disable redirects, retain exact bytes and stop on 429/repeated dead-instance evidence. Do not share mutable requests.Session state across threads. Cookies, tokens and full responses stay in local solve state and never enter reusable knowledge. Treat cross-origin OOB receivers as permitted only when explicitly assigned or owned and allowed by challenge rules.

## Differential interpretation

Compare a valid request, an inert marker and one minimal hypothesis-changing request. A 500 can indicate parser behavior or generic failure; it is not proof of exploitation. A 404 alone is not evidence of expiry. A regex-looking flag remains a candidate until its origin and actual checker semantics validate it. Keep rejected encodings, null-byte behavior and parser-version conditions in HYPOTHESES.md to avoid repeating failures.
