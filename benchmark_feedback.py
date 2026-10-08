"""Matched bounded comparison. Controls never count as live model evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from noetherpilot.provider import NebiusProvider, ControlProvider
from noetherpilot.research import run, replay

class WithheldFeedback:
    def __init__(self, provider):
        self.inner=provider;self.name=provider.name;self.live=provider.live
    def propose(self, problem, feedback):
        proposal,metadata=self.inner.propose(problem,[])
        return proposal,{**metadata,'exact_feedback_withheld':True}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--provider',choices=['nebius','control'],default='nebius');parser.add_argument('--repetitions',type=int,default=2);parser.add_argument('--out',type=Path,default=Path('evidence/feedback-comparison.json'));args=parser.parse_args()
    if not 1<=args.repetitions<=3:raise ValueError('Choose one to three matched repetitions')
    provider=NebiusProvider() if args.provider=='nebius' else ControlProvider()
    model=provider.select_model() if args.provider=='nebius' else None
    rows=[]
    for repetition in range(args.repetitions):
        arms=['exact_feedback','withheld_feedback'] if repetition%2==0 else ['withheld_feedback','exact_feedback']
        for arm in arms:
            receipt=run(provider if arm=='exact_feedback' else WithheldFeedback(provider),rounds=2);replay(receipt)
            usage=[e.get('provider_metadata',{}).get('usage',{}) for e in receipt['events']]
            rows.append({'repetition':repetition+1,'arm':arm,'status':receipt['status'],'live_successful_responses':receipt['live_runtime_calls'],
                         'reported_total_tokens':sum(u.get('total_tokens',0) for u in usage),'elapsed_seconds':receipt['elapsed_seconds'],'receipt':receipt})
    report={'generated_at':datetime.now(timezone.utc).isoformat(),'provider':args.provider,'model':model,'maximum_model_calls':4*args.repetitions,'maximum_output_tokens_per_call':900,'results':rows,
            'scope':'Same fixed known problem and model, two-round cap, alternating arm order. A small measured comparison is not historical novelty, provider attestation or an estimated win probability. Unreported failed-call token usage is unavailable.'}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'provider':args.provider,'model':model,'trials':len(rows),'certified_by_arm':{a:sum(r['status']=='CERTIFIED_RESULT' for r in rows if r['arm']==a) for a in ('exact_feedback','withheld_feedback')},'out':str(args.out)},indent=2))

if __name__=='__main__':main()
