#!/usr/bin/env python3
"""Kali-first category installer. Dry-run/verify never install or create a venv."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def selected_packages(manifest: dict, tiers: list[str]) -> tuple[dict, dict]:
    apt, python = {}, {}
    if 'all' in tiers:
        tiers = [name for name in manifest['tiers'] if name != 'heavy'] + (['heavy'] if 'heavy' in tiers else [])
    for tier in tiers:
        if tier not in manifest['tiers']:
            raise ValueError(f'unknown tier: {tier}')
        apt.update(manifest['tiers'][tier]['apt'])
        python.update(manifest['tiers'][tier]['python'])
    return apt, python


def apt_installed(package: str) -> bool:
    if not shutil.which('dpkg-query'):
        return False
    result = subprocess.run(['dpkg-query', '-W', '-f=${db:Status-Status}', package], capture_output=True, text=True)
    return result.returncode == 0 and result.stdout.strip() == 'installed'


def python_installed(interpreter: Path, package: str, module: str) -> bool:
    if not interpreter.is_file():
        return False
    code = 'import importlib,importlib.metadata; importlib.metadata.version(' + repr(package) + '); importlib.import_module(' + repr(module) + ')'
    result = subprocess.run([str(interpreter), '-c', code], capture_output=True, timeout=20)
    return result.returncode == 0


def resolve_sage(apt: dict, missing: list[str]) -> tuple[list[str], dict | None]:
    """Honor an existing Sage and diagnose snapshots without an apt candidate."""
    if 'sagemath' not in apt:
        return missing, None
    if shutil.which('sage'):
        return [name for name in missing if name != 'sagemath'], None
    if 'sagemath' in missing and shutil.which('apt-cache'):
        result = subprocess.run(['apt-cache', 'policy', 'sagemath'], capture_output=True, text=True,
            timeout=10, env={**os.environ, 'LC_ALL': 'C'})
        if result.returncode == 0 and ('Candidate: (none)' in result.stdout or not result.stdout.strip()):
            return [name for name in missing if name != 'sagemath'], {
                'tool': 'sage', 'reason': 'This apt snapshot has no sagemath candidate.',
                'fallback': 'Use an existing Sage environment, or conda create -n ctf-sage -c conda-forge sage; expose its sage command before retrying.',
                'documentation': 'https://doc.sagemath.org/html/en/installation/conda.html'}
    return missing, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tiers', nargs='*', default=['core'], help='core web pwn crypto reverse forensics osint malware misc ai-ml heavy; all excludes heavy')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--missing-only', action='store_true', help='default behavior; never reinstall healthy packages')
    parser.add_argument('--venv', type=Path, default=Path.home()/'.local/share/ctf-tools/venv')
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name('tool_manifest.json').read_text(encoding='utf-8'))
    try:
        apt, python = selected_packages(manifest, args.tiers or ['core'])
        interpreter = args.venv/'bin/python'
        missing_apt = [package for package, command in apt.items() if not apt_installed(package) or not shutil.which(command)]
        missing_apt, sage_setup = resolve_sage(apt, missing_apt)
        missing_python = [package for package, module in python.items() if not python_installed(interpreter, package, module)]
        commands = []
        if missing_apt:
            commands.append(([] if hasattr(os, 'geteuid') and os.geteuid() == 0 else ['sudo']) + ['apt-get', 'install', '-y', *missing_apt])
        if missing_python:
            if not interpreter.exists():
                commands.append([sys.executable, '-m', 'venv', str(args.venv)])
            commands.append([str(interpreter), '-m', 'pip', 'install', *missing_python])
        plan = {'tiers': args.tiers, 'missing_apt': missing_apt, 'missing_python': missing_python,
                'commands': commands, 'venv': str(args.venv), 'heavy_explicit': 'heavy' in args.tiers,
                'required_tools_setup': [sage_setup] if sage_setup else []}
        print(json.dumps(plan, indent=2), flush=True)
        if args.verify:
            return 1 if missing_apt or missing_python or sage_setup else 0
        if args.dry_run:
            return 0
        if sage_setup:
            print(sage_setup['reason'] + ' ' + sage_setup['fallback'], file=sys.stderr)
            return 2
        if missing_apt and not shutil.which('apt-get'):
            parser.error('installation requires Kali/Debian apt-get; use --dry-run on other hosts')
        for command in commands:
            result = subprocess.run(command, check=False)
            if result.returncode:
                print('Installation failed: ' + repr(command) + '; check apt package availability or Python/shared-library diagnostics', file=sys.stderr)
                return result.returncode
        failed = [name for name, module in python.items() if not python_installed(interpreter, name, module)]
        apt_failed, sage_after_install = resolve_sage(apt, [name for name, command in apt.items() if not apt_installed(name) or not shutil.which(command)])
        failed += apt_failed
        if sage_after_install:
            failed.append('sage (external setup required)')
        if failed:
            print('Installed package/tool verification failed: ' + ', '.join(failed), file=sys.stderr)
            return 1
        print('Tools ready.' + (' For Python workflows: source ' + str(args.venv/'bin/activate') if python else ''))
        return 0
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        parser.error(str(error))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
