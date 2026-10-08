import argparse
import json
from pathlib import Path
import sys
from .provider import NebiusProvider,ControlProvider,ProviderUnavailable
from .research import run,replay

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['run','replay','serve']);p.add_argument('--provider',choices=['nebius','control'],default='nebius');p.add_argument('--rounds',type=int,default=2);p.add_argument('--out',type=Path,default=Path('.state/research.json'));p.add_argument('--receipt',type=Path);p.add_argument('--port',type=int,default=4188);a=p.parse_args()
    if a.command=='serve':
        from .server import serve
        serve(a.port);return 0
    if a.command=='replay':print(json.dumps(replay(json.loads(a.receipt.read_text())),indent=2));return 0
    provider=NebiusProvider() if a.provider=='nebius' else ControlProvider();r=run(provider,a.rounds);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'provider_mode':r['provider_mode'],'live_runtime_calls':r['live_runtime_calls'],'receipt_id':r['receipt_id'],'output':str(a.out)},indent=2));return 0 if r['status']=='CERTIFIED_RESULT' else 2

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,ProviderUnavailable,OSError) as e:print(str(e),file=sys.stderr);raise SystemExit(2)
