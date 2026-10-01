import contextlib
import http.server
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

from instance_health import http_observation, assess

ROOT=Path(__file__).resolve().parents[1]


class Handler(http.server.BaseHTTPRequestHandler):
    seen=[]
    def log_message(self,*args): pass
    def do_GET(self):
        self.seen.append(self.path)
        if self.path == '/redirect':
            self.send_response(302);self.send_header('Location','/followed');self.end_headers();return
        if self.path == '/slow':
            self.send_response(200);self.end_headers()
            try:
                for _ in range(8):
                    self.wfile.write(b'x');self.wfile.flush();time.sleep(.3)
            except (BrokenPipeError,ConnectionResetError): pass
            return
        data=b'instance expired: default backend' if self.path=='/expired' else b'expected challenge'
        self.send_response(404 if self.path=='/expired' else 200)
        self.end_headers();self.wfile.write(data)


@contextlib.contextmanager
def server():
    Handler.seen=[]
    httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    httpd.daemon_threads=True
    thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
    try: yield f'http://127.0.0.1:{httpd.server_port}'
    finally: httpd.shutdown();httpd.server_close();thread.join(timeout=2)


def test_expected_marker_and_redirect_not_followed():
    with server() as url:
        result=http_observation(url,1,'expected challenge')
        assert assess([result])[0]=='application-reachable'
        result=http_observation(url+'/redirect',1,None)
        assert result['status']==302 and '/followed' not in Handler.seen
        assert result['sampled_bytes']<=4096


def test_health_cli_stops_after_two_expiry_checks(tmp_path):
    with server() as url:
        scope=tmp_path/'scope.json'
        scope.write_text(json.dumps({'kind':'challenge_instance','target':url+'/expired'}))
        result=subprocess.run([sys.executable,str(ROOT/'scripts/instance_health.py'),'--scope',str(scope),'--timeout','1'],capture_output=True,text=True,timeout=8)
        value=json.loads(result.stdout)
        assert result.returncode==3 and value['checks']==2
        assert Handler.seen==['/expired','/expired']
        assert 'Refresh/restart' in value['action']


def test_deadline_bounds_dripping_body_and_tls_stays_verified():
    with server() as url:
        start=time.monotonic()
        result=http_observation(url+'/slow',.4,None)
        assert time.monotonic()-start<2.2 and result['error']=='deadline'
        result=http_observation(url.replace('http:','https:'),.5,None)
        assert result['error']=='tls' and assess([result])[0]=='inconclusive'
