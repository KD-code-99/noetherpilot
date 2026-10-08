from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"vendor"))
from noetherforge import algebra as A
from noetherforge.rational import RationalGoal
from noetherforge.proofcheck import verify
from .provider import ProviderUnavailable

PROBLEM={"id":"lyness-symbolic","variables":["x","y","a"],"transitions":["y","(a+y)/x","a"],"parameters":["a"],"domain":"Rationals where the original recurrence and candidate are defined","question":"Find a nonconstant rational state invariant for the declared map, uniformly in the fixed parameter a."}


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def bounded(text):
    if not isinstance(text,str) or not 0<len(text)<=400:raise ValueError('Proposal expressions must contain 1–400 characters')
    tree=ast.parse(text,mode='eval')
    if sum(1 for _ in ast.walk(tree))>100:raise ValueError('Proposal syntax exceeds the limit')
    if any(isinstance(n,(ast.Call,ast.Attribute,ast.Subscript,ast.Lambda)) for n in ast.walk(tree)):raise ValueError('Model expressions are data; executable code is forbidden')
    for n in ast.walk(tree):
        if isinstance(n,ast.BinOp) and isinstance(n.op,ast.Pow):
            if not isinstance(n.right,ast.Constant) or type(n.right.value) is not int or not 0<=n.right.value<=6 or any(isinstance(p,ast.BinOp) and isinstance(p.op,ast.Pow) for p in ast.walk(n.left)):
                raise ValueError('Use a literal power from 0 to 6 without nested powers')
        if isinstance(n,ast.Constant) and (type(n.value) is not int or abs(n.value)>10**12):raise ValueError('Only small exact integer literals are supported')
    return text


def inspect(proposal):
    n=bounded(proposal['numerator']);d=bounded(proposal['denominator'])
    if not isinstance(proposal.get('motivation'),str) or not proposal['motivation'].strip():raise ValueError('A proposal must explain its mechanism')
    goal=RationalGoal(PROBLEM['id'],PROBLEM['variables'],PROBLEM['transitions'],4,2,('a',))
    certificate=goal.certificate(A.parse(n,goal.variables),A.parse(d,goal.variables))
    verdict=verify(certificate)
    return {'proposal':proposal,'certificate':certificate,'verification':verdict,'status':verdict['status']}


def run(provider, rounds=2, on_event=None):
    if type(rounds) is not int or not 1<=rounds<=3:raise ValueError('Choose one to three model rounds')
    events=[];feedback=[];started=time.perf_counter()
    def append(event):
        event={**event,'event_id':len(events)+1};events.append(event)
        if on_event:on_event(event)
    initial={'numerator':'x+y','denominator':'1','motivation':'User-supplied seed hypothesis for testing; this is not model output.'}
    seed=inspect(initial);append({'phase':'seed_check','source':'user_seed',**seed})
    feedback.append({'proposal':initial,'verification':seed['verification'],'instruction':'Use the exact counterexample to change the next proposal.'})
    certified=False;live_calls=0
    for round_id in range(1,rounds+1):
        append({'phase':'model_request','round':round_id,'provider':provider.name,'live':provider.live})
        try:
            proposal,metadata=provider.propose(PROBLEM,feedback)
            if metadata.get('live_runtime_call'):live_calls+=1
            try:
                checked=inspect(proposal)
                append({'phase':'proposal_check','round':round_id,'source':provider.name,'provider_metadata':metadata,**checked})
            except (ValueError,KeyError,TypeError,SyntaxError,RuntimeError) as error:
                checked={'status':'INVALID_PROPOSAL','reason':str(error)[:250]}
                append({'phase':'proposal_check','round':round_id,'provider_metadata':metadata,'proposal':proposal,**checked})
            feedback.append({'round':round_id,'result':checked})
            if checked['status']=='CERTIFIED_RATIONAL_INVARIANT':certified=True;break
        except ProviderUnavailable as error:
            append({'phase':'provider_error','round':round_id,'status':'PROVIDER_UNAVAILABLE','reason':str(error)})
            break
    body={'schema_version':1,'problem':PROBLEM,'provider':provider.name,'provider_mode':'LIVE_NVIDIA' if provider.live else 'PROVIDER_CONTRACT_FIXTURE' if provider.name=='provider_contract_fixture' else 'DETERMINISTIC_CONTROL',
          'status':'CERTIFIED_RESULT' if certified else 'NO_CERTIFIED_RESULT','live_runtime_calls':live_calls,'events':events,
          'scope':'Supported rational invariants on the declared domain. Known controls do not establish historical novelty. A deterministic control does not satisfy the hackathon platform requirement.',
          'engine_sha256':{n:hashlib.sha256((ROOT/'vendor/noetherforge'/n).read_bytes()).hexdigest() for n in ('proofcheck.py','verifier.py','rational.py','algebra.py')},
          'elapsed_seconds':round(time.perf_counter()-started,6)}
    return {**body,'receipt_id':hashlib.sha256(canonical(body)).hexdigest()}


def replay(receipt):
    body={k:v for k,v in receipt.items() if k!='receipt_id'}
    if hashlib.sha256(canonical(body)).hexdigest()!=receipt['receipt_id']:raise ValueError('The research receipt was changed')
    if receipt['problem']!=PROBLEM:raise ValueError('The receipt describes a different research problem')
    if set(receipt['engine_sha256'])!={'proofcheck.py','verifier.py','rational.py','algebra.py'}:raise ValueError('The receipt omits a checking engine')
    for name,digest in receipt['engine_sha256'].items():
        if name not in ('proofcheck.py','verifier.py','rational.py','algebra.py') or hashlib.sha256((ROOT/'vendor/noetherforge'/name).read_bytes()).hexdigest()!=digest:raise ValueError('The checking engine differs')
    checks=0
    for event in receipt['events']:
        if 'certificate' in event:
            reconstructed=inspect(event['proposal'])
            if canonical(reconstructed['certificate'])!=canonical(event['certificate']):raise ValueError('A certificate is not bound to the declared problem and proposal')
            if verify(event['certificate'])!=event['verification']:raise ValueError('Mathematical evidence did not replay')
            checks+=1
    if receipt['status']=='CERTIFIED_RESULT' and not any(e.get('status')=='CERTIFIED_RATIONAL_INVARIANT' for e in receipt['events']):raise ValueError('Certified summary has no mathematical proof')
    return {'status':'REPLAY_PASSED','mathematical_checks':checks,'provider_mode':receipt['provider_mode'],
            'provider_execution_reperformed':False,'scope':'Replays mathematical evidence and receipt integrity, not a new model call or provider attestation.'}
