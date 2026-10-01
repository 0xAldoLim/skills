# Kali tool strategy

Run the bundle's helpers by their resolved installation path, not relative to the challenge directory. Installed category symlinks resolve back to the complete checkout.

```sh
python3 <bundle>/scripts/install_tools.py core web --dry-run
python3 <bundle>/scripts/install_tools.py core web --missing-only
python3 <bundle>/scripts/install_tools.py crypto --verify
python3 <bundle>/scripts/install_tools.py all --dry-run
# Heavy packages are explicitly selected:
python3 <bundle>/scripts/install_tools.py heavy --dry-run
```

The installer checks dpkg status, Python distribution metadata and actual module imports. It installs missing apt packages and creates an isolated Python venv, respecting Kali's externally managed system Python. It never uses sudo pip, curl-to-shell, or automatic heavy category dependencies. A package failure includes its command and keeps the plan reviewable. It does not run apt update automatically; refresh stale repository metadata when diagnostics justify it. Tool/package availability varies by Kali snapshot: verify rather than assuming installation succeeded.

| Need | Cheap/default | Fallback / heavy step |
|---|---|---|
| Native triage | file, strings, readelf, objdump | radare2; Ghidra after targeted static inspection |
| Debug/exploit | gdb, pwntools in venv | architecture-matched QEMU in a dedicated local environment |
| Number theory | stdlib exact integers, sympy, gmpy2 | Sage when field/ring arithmetic requires it |
| Lattice reduction | fpylll/cysignals with native dependencies | Sage or a separately verified flatter build |
| Disassembly/emulation | capstone, unicorn | targeted architecture/toolchain setup |
| Symbolic constraints | z3-solver | angr only when bounded constraints or targeted emulation are insufficient |
| Capture / memory | tshark, scapy; Volatility 3 | older Volatility 2 only for a supported artifact/plugin need |
| Archive / document | guarded ZIP/TAR helper, 7z, oletools | dedicated parser harness for traversal/polyglot hypotheses |
| Images/audio | Pillow, ffmpeg, sox | bounded OCR/model or GNU Radio workflow |
| ML metadata | safetensors, h5py, NumPy | PyTorch/TensorFlow/Transformers in isolated heavy tier |
| Public OSINT | text, EXIF, public page metadata | precise human visual question when machine evidence stays ambiguous |

Examples:

```sh
python3 <bundle>/scripts/triage_artifacts.py . --max-files 100
python3 <bundle>/scripts/extract_archive.py supplied.zip --output work/unpacked
python3 <bundle>/scripts/crypto_helpers.py --help
python3 <bundle>/scripts/pwn_payloads.py --help
python3 <bundle>/ctf-web/scripts/async_fuzz.py --help
```

Crypto helpers use exact arithmetic and verify candidates; they do not contact instances. Payload builders require measured offsets/addresses and produce local data, not exploits that automatically run. Archive extraction refuses links/traversal/devices and expanded-size excess. For intentionally malicious archive behavior, build a dedicated disposable reproduction rather than disabling the general extractor's guards. A dependency or GPU failure is a tool setup issue, not evidence that a challenge is unsolvable.

Validation exercised the core apt installer and the full helper suite on Kali 2026.3 / Python 3.14.7, including pwntools payload ABI checks. Windows portable tests also passed. Heavy numerical/GPU/SDR stacks and full historical challenge exploit reproductions remain separate validation tasks.

## Rolling package changes

The current Kali [7zip package](https://www.kali.org/tools/7zip/) provides 7z; the manifest uses it instead of the older p7zip-full name. [Ghidra](https://www.kali.org/tools/ghidra/) remains an apt package. Sage availability varies across Debian/Kali snapshots: inspect apt-cache policy sagemath before the heavy tier. If no candidate exists, use an already configured Sage environment or the official [conda-forge installation](https://doc.sagemath.org/html/en/installation/conda.html), for example `conda create -n ctf-sage -c conda-forge sage`, then `conda run -n ctf-sage sage --version`. This is a deliberate heavy fallback, not a missing-only lightweight install. Never run a downloaded shell installer just because a package name failed.

On the tested Kali snapshot, Python 3.14 caused pwntools' Unicorn dependency to build from source. The pwn and reverse tiers include gcc, g++, make, cmake and pkg-config for this route; metadata-only categories do not install a compiler. Other native Python libraries may require their own development packages when no compatible wheel exists. Read the actual build error and install the named prerequisites rather than weakening version constraints blindly.

Kali 2026.3 had no sagemath apt candidate. The installer detects this and reports the conda fallback in its plan; --verify stays unsuccessful until Sage is available. An installation request stops with that actionable diagnostic before starting the other large packages. An existing sage command is accepted even when it comes from another environment. [Unicorn's build instructions](https://github.com/unicorn-engine/unicorn/blob/master/docs/COMPILE.md) document CMake and pkg-config for native bindings.
