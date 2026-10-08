import copy
import os
import unittest
from unittest.mock import patch
from fractions import Fraction
from noetherpilot.provider import ControlProvider,NebiusProvider,ProviderUnavailable
from noetherpilot.research import run,replay,inspect

class ResearchTests(unittest.TestCase):
    def test_seed_is_refuted_before_control_proposal(self):
        r=run(ControlProvider());self.assertEqual(r['provider_mode'],'DETERMINISTIC_CONTROL');self.assertEqual(r['live_runtime_calls'],0)
        self.assertEqual(r['events'][0]['status'],'REFUTED');self.assertEqual(r['events'][-1]['status'],'CERTIFIED_RATIONAL_INVARIANT')
        p={k:Fraction(v) for k,v in r['events'][0]['verification']['counterexample'].items()};self.assertNotEqual(p['x']+p['y'],p['y']+(p['a']+p['y'])/p['x'])
        self.assertEqual(replay(r)['mathematical_checks'],2)
    def test_provider_receives_actual_counterexample(self):
        class Observer(ControlProvider):
            def propose(self,problem,feedback):
                self.last=feedback
                return super().propose(problem,feedback)
        p=Observer();run(p);self.assertEqual(p.last[0]['verification']['status'],'REFUTED');self.assertIn('counterexample',p.last[0]['verification'])
    def test_missing_key_is_not_silently_replaced(self):
        with patch.dict(os.environ,{'NEBIUS_API_KEY':''}),self.assertRaises(ProviderUnavailable):NebiusProvider()
    def test_catalog_and_payload_use_actual_nvidia_model(self):
        requests=[]
        def transport(path,payload=None):
            requests.append((path,payload))
            if path=='models':return {'data':[{'id':'other/model'},{'id':'nvidia/test-nemotron-nano'}]}
            return {'id':'fixture-only','model':'nvidia/test-nemotron-nano','choices':[{'message':{'content':'{"numerator":"(x+1)*(y+1)*(x+y+a)","denominator":"x*y","motivation":"fixture"}'}}],'usage':{'total_tokens':100}}
        with patch.dict(os.environ,{'NEBIUS_API_KEY':'test-only-not-a-real-key','NEBIUS_MODEL':''}):
            r=run(NebiusProvider(transport=transport))
        self.assertEqual(requests[1][1]['model'],'nvidia/test-nemotron-nano');self.assertEqual(requests[1][1]['max_tokens'],900)
        self.assertNotIn('test-only-not-a-real-key',str(r));self.assertEqual(r['status'],'CERTIFIED_RESULT')
    def test_non_nvidia_model_is_rejected(self):
        with patch.dict(os.environ,{'NEBIUS_API_KEY':'fixture','NEBIUS_MODEL':'other/model'}):
            p=NebiusProvider(transport=lambda *a:{'data':[{'id':'other/model'}]})
            with self.assertRaises(ProviderUnavailable):p.select_model()
    def test_proposed_code_and_receipt_corruption_are_rejected(self):
        with self.assertRaises(ValueError):inspect({'numerator':"__import__('os').getcwd()",'denominator':'1','motivation':'code'})
        r=run(ControlProvider());r['events'][0]['verification']['counterexample']['x']='99'
        with self.assertRaises(ValueError):replay(r)

if __name__=='__main__':unittest.main()
