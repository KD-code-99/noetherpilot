import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch
from noetherpilot.server import make_server
from noetherpilot.research import bounded


class ApplicationTests(unittest.TestCase):
    def test_browser_control_runs_replays_and_persists_actual_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ,{'NEBIUS_API_KEY':''}):
            server=make_server(0,Path(tmp));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            base=f'http://127.0.0.1:{server.server_port}'
            def post(path,data,origin=None):
                headers={'Content-Type':'application/json'}
                if origin:headers['Origin']=origin
                return urllib.request.urlopen(urllib.request.Request(base+path,json.dumps(data).encode(),headers))
            try:
                with urllib.request.urlopen(base+'/api/status') as response:self.assertFalse(json.load(response)['nebius_key_configured'])
                with self.assertRaises(urllib.error.HTTPError) as error:post('/api/research',{'provider':'nebius'})
                self.assertEqual(error.exception.code,422)
                with post('/api/research',{'provider':'control','rounds':2}) as response:identity=json.load(response)['job_id']
                for _ in range(200):
                    with urllib.request.urlopen(base+'/api/jobs/'+identity) as response:job=json.load(response)
                    if job['status']!='running':break
                    time.sleep(.1)
                self.assertEqual(job['status'],'complete');self.assertEqual(job['receipt']['live_runtime_calls'],0)
                self.assertEqual(json.loads((Path(tmp)/(identity+'.json')).read_text()),job['receipt'])
                with post('/api/replay',{'receipt':job['receipt']}) as response:self.assertEqual(json.load(response)['mathematical_checks'],2)
                with self.assertRaises(urllib.error.HTTPError) as error:post('/api/research',{'provider':'control'},'https://foreign.example')
                self.assertEqual(error.exception.code,403)
            finally:server.shutdown();server.server_close();thread.join()

    def test_expression_budget_rejects_power_towers(self):
        for expression in ('x**1000000000','((2**6)**6)**6','x**-1'):
            with self.assertRaises(ValueError):bounded(expression)
