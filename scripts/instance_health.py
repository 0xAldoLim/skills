#!/usr/bin/env python3
"""Bounded health checks of an explicitly assigned endpoint; no redirects or scans."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
import ssl
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def endpoint(value: str) -> tuple[str, str, int]:
    url = urlsplit(value if '://' in value else 'tcp://' + value)
    if url.scheme not in {'http', 'https', 'tcp'} or not url.hostname or url.username or url.password:
        raise ValueError('use http(s)://host[:port]/path or host:port without credentials')
    port = url.port or {'http': 80, 'https': 443}.get(url.scheme)
    if not port or not 0 < port < 65536:
        raise ValueError('TCP target requires an explicit valid port')
    if any(c in url.hostname for c in ('*', '/', ',')):
        raise ValueError('wildcards, ranges and target lists are not allowed')
    return url.scheme, url.hostname.lower(), port


def scoped_urls(scope: dict, routes: list[str]) -> list[str]:
    if scope.get('kind') != 'challenge_instance':
        raise ValueError('scope kind must explicitly be challenge_instance')
    target = str(scope.get('target', ''))
    exact = endpoint(target)
    if len(routes) > 2:
        raise ValueError('health budget is baseline plus at most two known routes')
    urls = [target]
    for route in routes:
        if exact[0] == 'tcp':
            raise ValueError('known routes are only for HTTP')
        candidate = urljoin(target, route)
        if endpoint(candidate) != exact:
            raise ValueError('known route leaves the explicitly supplied origin')
        if candidate not in urls:
            urls.append(candidate)
    return urls


def _http_observation(url: str, timeout: float, expected: str | None) -> dict:
    opener = build_opener(NoRedirect())
    observation = {'transport': 'http', 'status': None, 'error': None}
    try:
        try:
            response = opener.open(Request(url, headers={'User-Agent': 'CTF-instance-health/1.0'}), timeout=timeout)
        except HTTPError as error:
            response = error
        with response:
            data = response.read(4096)
            text = data.decode('utf-8', errors='replace')
            body = text.lower()
            observation.update(status=response.code, body_sha256=hashlib.sha256(data).hexdigest(),
                               sampled_bytes=len(data), server=response.headers.get('Server', ''),
                               expected_marker=bool(expected and expected in text),
                               redirect=response.headers.get('Location') is not None,
                               proxy_marker=any(x in body for x in ('default backend', 'no backend available',
                                    'upstream unavailable', 'container not found', 'deployment not found',
                                    'application not found', 'instance expired', 'challenge stopped', 'invalid instance',
                                    'bad gateway', 'service unavailable', 'gateway timeout')))
    except (URLError, OSError, ssl.SSLError, ValueError) as error:
        reason = getattr(error, 'reason', error)
        observation['error'] = 'tls' if isinstance(reason, ssl.SSLError) else type(reason).__name__
    return observation


def _tcp_observation(target: str, timeout: float, probe: bytes, expected: str | None) -> dict:
    _, host, port = endpoint(target)
    observation = {'transport': 'tcp', 'connected': False, 'error': None}
    try:
        with socket.create_connection((host, port), timeout=timeout) as connection:
            observation['connected'] = True
            if probe:
                connection.sendall(probe)
            try:
                data = connection.recv(4096)
            except socket.timeout:
                data = b''
            observation.update(sampled_bytes=len(data), body_sha256=hashlib.sha256(data).hexdigest(),
                               expected_marker=bool(expected and expected.encode() in data))
    except OSError as error:
        observation['error'] = type(error).__name__
    return observation


def bounded_observation(kind: str, target: str, timeout: float, expected: str | None, probe: bytes = b'') -> dict:
    # A process deadline bounds DNS resolution and slow/dripping bodies too.
    # Pass payload via stdin, rather than putting challenge secrets in argv.
    endpoint(target)
    request = json.dumps({'kind': kind, 'target': target, 'timeout': timeout, 'expected': expected, 'probe': probe.hex()})
    try:
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--observation-worker'],
                                input=request, capture_output=True, text=True, timeout=timeout + 1)
        if result.returncode:
            return {'transport': kind, 'error': 'worker-error', 'status': None}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {'transport': kind, 'error': 'deadline', 'status': None}


def http_observation(url: str, timeout: float, expected: str | None) -> dict:
    return bounded_observation('http', url, timeout, expected)


def tcp_observation(target: str, timeout: float, probe: bytes, expected: str | None) -> dict:
    return bounded_observation('tcp', target, timeout, expected, probe)


def assess(observations: list[dict]) -> tuple[str, list[str]]:
    if any(o.get('expected_marker') for o in observations):
        return 'application-reachable', ['Expected application/protocol marker observed']
    if any(o.get('error') == 'tls' for o in observations):
        return 'inconclusive', ['TLS validation/configuration failed; check the supplied endpoint']
    if observations and all(o.get('error') for o in observations) and len(observations) >= 2:
        return 'likely-unavailable', ['Minimal repeated connection checks failed; distinguish local network failure']
    if any(o.get('connected') and o.get('sampled_bytes', 0) for o in observations):
        return 'reachable-unconfirmed', ['TCP response observed; verify expected protocol']
    proxy = [o for o in observations if o.get('proxy_marker') and o.get('status') in {404, 410, 502, 503, 504}]
    if len(proxy) >= 2:
        return 'likely-unavailable', ['Repeated generic infrastructure error without expected application content']
    if any(o.get('status') is not None and 200 <= o['status'] < 300 and not o.get('proxy_marker') for o in observations):
        return 'reachable-unconfirmed', ['HTTP response observed; verify challenge content rather than a placeholder']
    return 'inconclusive', ['Single errors, deliberate 404/500, redirects and silent TCP require a known discriminator']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', type=Path, required=True)
    parser.add_argument('--known-route', action='append', default=[])
    parser.add_argument('--expected', help='Known application or protocol marker')
    parser.add_argument('--timeout', type=float, default=3.0)
    parser.add_argument('--probe-hex', default='', help='Optional TCP protocol message, at most 128 bytes')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        if not 0 < args.timeout <= 10:
            raise ValueError('timeout must be between 0 and 10 seconds')
        scope = json.loads(args.scope.read_text(encoding='utf-8'))
        urls = scoped_urls(scope, args.known_route)
        probe = bytes.fromhex(args.probe_hex)
        if len(probe) > 128:
            raise ValueError('TCP probe budget is 128 bytes')
        scheme = endpoint(urls[0])[0]
        if scheme != 'tcp' and probe:
            raise ValueError('--probe-hex is only for TCP')
        check = (lambda url: tcp_observation(url, args.timeout, probe, args.expected)) if scheme == 'tcp' else (
            lambda url: http_observation(url, args.timeout, args.expected))
        observations = [check(url) for url in urls]
        status, evidence = assess(observations)
        if status == 'inconclusive' and len(observations) == 1 and (
                observations[0].get('error') or observations[0].get('proxy_marker')):
            observations.append(check(urls[0]))
            status, evidence = assess(observations)
        result = {'status': status, 'evidence': evidence, 'checks': len(observations), 'observations': observations,
                  'action': 'Refresh/restart the instance and provide the new URL/host; preserve solve state'
                            if status == 'likely-unavailable' else 'Use description/source to confirm application behavior'}
        rendered = json.dumps(result, indent=2) + '\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding='utf-8')
        print(rendered, end='')
        return 3 if status == 'likely-unavailable' else 0
    except (ValueError, OSError) as error:
        parser.error(str(error))
        return 2


if __name__ == '__main__':
    if sys.argv[1:] == ['--observation-worker']:
        value = json.load(sys.stdin)
        function = _http_observation if value['kind'] == 'http' else _tcp_observation
        if value['kind'] == 'http':
            result = function(value['target'], value['timeout'], value['expected'])
        else:
            result = function(value['target'], value['timeout'], bytes.fromhex(value['probe']), value['expected'])
        print(json.dumps(result))
    else:
        raise SystemExit(main())
