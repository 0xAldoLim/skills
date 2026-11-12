# Reviewed pwntools payload templates

These files are reference templates adapted from
[`ljagiello/ctf-skills`](https://github.com/ljagiello/ctf-skills) commit
`e79be2925d1612e8a97070d6201e300286672370` (MIT). They are not executed
automatically and they are not a substitute for analyzing the target.

## Safety contract

- Use them only against an **authorized local challenge instance** or the exact
  assigned remote endpoint. Never point `HOST`/`REMOTE` at CTFd, scoreboards,
  organizer systems, shared competition infrastructure or another team's target.
- Defaults are localhost and a local binary. `args.REMOTE` is opt-in.
- Every address and offset is a placeholder; derive it from the actual target.
- Review the script before running it. It may launch a process, connect to a
  socket, or write files in the current directory.
- Keep flags, candidate values and transcripts out of public repositories.

## Files

| File | Use |
| --- | --- |
| `fmtstr_payload_suite.py` | Format-string leak and write payload variants |
| `ret2libc_two_stage.py` | Leak libc, then ret2system/ret2libc |
| `seccomp_orw_generator.py` | Open/read/write shellcode variants |
| `shellcraft_asm.py` | Shellcraft shellcode variants and constraints |
| `srop_execve.py` | Sigreturn-oriented programming frames |
