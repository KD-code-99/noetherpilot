from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
import re
import threading
import uuid
from urllib.parse import urlparse
from .provider import ControlProvider,NebiusProvider,ProviderUnavailable
from .research import ROOT,run,replay

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def reply(self,code,body,kind='application/json'):
        raw=body if isinstance(body,bytes) else json.dumps(body,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(raw)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(raw)
    def allowed(self):
        host=self.headers.get('Host');origin=self.headers.get('Origin');return host in self.server.hosts and (not origin or urlparse(origin).netloc==host)
    def do_GET(self):
        if not self.allowed():return self.reply(403,{'error':'Unsupported origin or host'})
        path=urlparse(self.path).path
        if path=='/api/status':return self.reply(200,{'nebius_key_configured':bool(os.environ.get('NEBIUS_API_KEY')),'model_override':os.environ.get('NEBIUS_MODEL') or None,'live_run_verified':False})
        if path.startswith('/api/jobs/'):
            identity=path.rsplit('/',1)[1]
            with self.server.lock:
                found=self.server.jobs.get(identity)
                r=json.loads(json.dumps(found)) if found else None
            return self.reply(200 if r else 404,r or {'error':'Run not found'})
        assets={'/':'index.html','/app.js':'app.js','/style.css':'style.css','/favicon.svg':'favicon.svg'}
        if path not in assets:return self.reply(404,{'error':'Not found'})
        f=ROOT/'web'/assets[path];kind={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml'}[f.suffix];return self.reply(200,f.read_bytes(),kind)
    def do_POST(self):
        if not self.allowed():return self.reply(403,{'error':'Unsupported origin or host'})
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0<size<=32768:raise ValueError('Request size limit')
            data=json.loads(self.rfile.read(size))
            if self.path=='/api/replay':return self.reply(200,replay(data['receipt']))
            if self.path!='/api/research':return self.reply(404,{'error':'Not found'})
            mode=data.get('provider','nebius');rounds=data.get('rounds',2)
            if mode not in ('nebius','control') or type(rounds) is not int or not 1<=rounds<=3:raise ValueError('Invalid provider or round count')
            provider=NebiusProvider() if mode=='nebius' else ControlProvider()
            with self.server.lock:
                if any(v['status']=='running' for v in self.server.jobs.values()):return self.reply(409,{'error':'A research run is already active'})
                identity=uuid.uuid4().hex;self.server.jobs[identity]={'id':identity,'status':'running','events':[],'provider':mode}
            def update(event):
                with self.server.lock:self.server.jobs[identity]['events'].append(event)
            def worker():
                try:
                    receipt=run(provider,rounds,update)
                    self.server.state.mkdir(parents=True,exist_ok=True);(self.server.state/(identity+'.json')).write_text(json.dumps(receipt,indent=2),encoding='utf-8')
                    with self.server.lock:self.server.jobs[identity].update({'status':'complete','receipt':receipt})
                except Exception as error:
                    with self.server.lock:self.server.jobs[identity].update({'status':'error','error':str(error)[:250]})
            threading.Thread(target=worker,daemon=True).start()
            return self.reply(202,{'job_id':identity})
        except (ValueError,KeyError,TypeError,ProviderUnavailable) as error:return self.reply(422,{'error':str(error)[:350]})

def make_server(port=4188,state=None):
    s=ThreadingHTTPServer(('127.0.0.1',port),Handler);s.hosts={f'127.0.0.1:{s.server_port}',f'localhost:{s.server_port}'};s.jobs={};s.lock=threading.Lock();s.state=state or ROOT/'.state'/'runs';return s

def serve(port=4188):
    server=make_server(port)
    print(f'NoetherPilot: http://127.0.0.1:{server.server_port}',flush=True)
    server.serve_forever()

def serve(port=4188):
    s=make_server(port);print(f'NoetherPilot http://127.0.0.1:{s.server_port}',flush=True);s.serve_forever()
