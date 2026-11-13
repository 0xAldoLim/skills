# Tooling: tiers, fallbacks, isolation

Use what is already installed. Install a tier only when the current hypothesis needs it. Do not download gigabytes for a simple challenge.

## Tiers

| Tier | Contents | When |
|---|---|---|
| Core | file, binutils, git, curl, jq, ripgrep, Python venv, pipx | Always useful |
| Category | web/pwn/crypto/reverse/forensics/OSINT/malware/misc/AI-ML packages | Selected from evidence |
| Advanced | Sage, Ghidra, QEMU, GNU Radio, angr, PyTorch/TensorFlow | Explicit need only |
| Heavy | Large model/runtime stacks | Explicit request; verify disk/GPU first |

```bash
python3 "$REPO_ROOT/scripts/install_tools.py" core web --dry-run
python3 "$REPO_ROOT/scripts/install_tools.py" core web --missing-only
python3 "$REPO_ROOT/scripts/install_tools.py" crypto --verify
python3 "$REPO_ROOT/scripts/install_tools.py" --doctor
python3 "$REPO_ROOT/scripts/install_tools.py" heavy --dry-run
source ~/.local/share/ctf-tools/venv/bin/activate
```

`--missing-only` avoids reinstalling healthy packages. `--verify` checks without installing. `--dry-run` prints the plan and never creates a venv. `all` excludes heavy; add `heavy` explicitly. `--doctor` reports platform/package-manager readiness and missing selected tools.

## Cross-platform

- **Kali/Linux:** apt + isolated venv. Do not use `sudo pip`.
- **WSL:** use the Linux instructions inside the WSL distribution; do not mix Windows Python with Linux packages.
- **Windows:** offline artifacts and pure-Python work are supported. `--dry-run`/`--doctor` work; apt installs require WSL or a Linux VM. Use PowerShell for file handling and a Linux environment for ELF/pwn/kernel work.
- **macOS:** use Homebrew/venv equivalents; the installer will report apt unavailability rather than silently failing.

## Fallback ladder

| Need | Default | Fallback |
|---|---|---|
| Native triage | file, strings, readelf, objdump | radare2/rizin; Ghidra headless after targeted inspection |
| Debug/exploit | gdb, pwntools | architecture-matched QEMU |
| Number theory | Python ints, sympy, gmpy2 | Sage for fields/curves/lattices |
| Lattice | fpylll | Sage/flatter |
| Disassembly/emulation | capstone/unicorn | targeted QEMU or reimplementation |
| Constraints | z3-solver | bounded brute force or custom search |
| Capture | tshark/scapy | tcpdump + custom parser |
| Memory | Volatility 3 | strings/carving with limits |
| Documents | format parser, 7z, oletools | dedicated parser harness |
| Images/audio | Pillow/ffmpeg/sox | bounded OCR/model or GNU Radio |
| ML metadata | safetensors/h5py/numpy | PyTorch/Transformers in the heavy tier |

## Isolation

- Never execute an unknown challenge binary on the development host.
- Use an isolated VM/container without provider credentials, a Docker socket or host mounts.
- Emulate malware/C2 locally; do not contact real infrastructure.
- Inspect static code and archive structure before running anything.
- For kernel/VM work, use a dedicated disposable environment.

Full details: [docs/TOOLS.md](../../docs/TOOLS.md).
