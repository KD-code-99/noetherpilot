# NoetherPilot: conjecture, refute, refine

### ⏳ Not submitted yet
Nothing has been sent to Devpost.

Local draft for a solo entry. Intended track: Best Apps and Agents. Official form labels and required answers remain unverified while the requirements service is unavailable; the sections below are prepared copy, not an invented form schema. The working local control and public test build are complete. Authenticated NVIDIA runtime evidence and public video hosting remain pending.

## One-line summary

Turn a wrong mathematical guess into an exact counterexample, a checked correction and a research receipt anyone can replay.

## Inspiration and problem

A plausible conservation law can survive a few numerical examples and still be false. Researchers exploring rational dynamical systems need to see exactly where a hypothesis fails, use that failure in the next attempt, and check a surviving expression independently of its proposer.

I already had NOETHER-FORGE's exact checking kernel. For this event, I built the product around that kernel: a bounded proposal loop, actual counterexample feedback, a visible research log and downloadable evidence. A fluent explanation is a proposal; the mathematical verdict comes from separate arithmetic.

## What it does

The current problem is the symbolic Lyness recurrence `(x,y,a) -> (y,(a+y)/x,a)`, with `a` fixed. The local demonstration follows four inspectable steps:

1. **Refute the seed.** The user seed `x+y` fails at `x=1, y=0, a=0`: its value changes from `1` to `0` in one admissible step. The exact witness and both values remain in the log.
2. **Use the failure.** The proposal interface receives that actual counterexample, the declared recurrence and the instruction to revise the next hypothesis. The acceptance suite checks that the proposer receives the witness.
3. **Check the next candidate independently.** The labelled deterministic control supplies the known expression `(x+1)*(y+1)*(x+y+a)/(x*y)`. The kernel reconstructs the rational identity and checks it with its required nonzero guards. This candidate has a different guarded domain from the failed seed; I do not claim it is defined at the seed's counterexample.
4. **Download and replay.** A research receipt retains the failed seed, proposal, certificate, verdict and checking-engine hashes. Replay reconstructs the mathematical obligations and rechecks both results. A changed receipt or different checking engine is rejected.

The browser runs this workflow and offers its actual evidence for download. Failed, invalid and unavailable-provider outcomes remain visible. Generated expressions are parsed as bounded data; generated code is never executed.

## Nebius and NVIDIA integration

The implemented adapter fetches Nebius Token Factory's authenticated model catalog and accepts only a returned model identity in the `nvidia/` namespace, preferring an available Nano model. It sends structured JSON proposals through chat completions and retains returned model identity, response identity and usage metadata. The default loop permits at most two proposal calls, with 900 output tokens per request, and stops when a supported candidate is certified.

**No authenticated NVIDIA model call has occurred.** The adapter is implemented and covered by labelled HTTP contract fixtures, which count as zero live calls. A missing key remains a provider error and never silently becomes the deterministic control. The recorded demo is explicitly local control execution. Live platform integration remains pending; these artifacts do not establish it.

## Results and why this matters

Eight local acceptance tests pass. They cover the seed-first workflow, actual counterexample feedback, NVIDIA catalog and payload handling through a fixture, rejection of a non-NVIDIA model, missing-key behavior, rejection of executable proposals and corrupted receipts, expression-budget enforcement, and the browser's persisted run and replay. The retained browser check records no JavaScript errors or horizontal overflow at widths 320, 768, 1024 and 1440 pixels.

The paired experiment executed so far uses the deterministic control: one certified result with exact feedback and one with feedback withheld, with zero live responses in both arms. **It establishes no model improvement.** I report no measured model quality, provider latency, live token cost or user adoption.

The demonstrated value is an inspectable research process: a wrong claim becomes a reusable counterexample, and a surviving supported claim carries evidence another person can recompute. The known Lyness formula is a control, not an original mathematical discovery.

## How I built it and used AI

I am entering solo. Codex assisted implementation, testing and documentation. The event work adds the Token Factory adapter, bounded feedback loop, browser research log, provider/control labels and source-bound receipt replay. The pre-existing Apache-2.0 kernel and copied-file provenance are retained with their original notices.

In the intended live workflow, an NVIDIA model proposes expressions and receives checked feedback. It does not supply the verdict. In the executed demo, the proposer is the labelled deterministic control. No model discovery is claimed from that execution.

## Architecture and scope

The Python 3.12 application has no third-party runtime dependencies. A local HTTP interface starts a bounded research job, the provider proposes a rational expression, the exact kernel constructs and independently verifies its certificate, and the log becomes a replayable JSON receipt. Replay performs no new provider call and does not attest that a cloud response occurred.

The supported task is the declared small rational recurrence and supported expression grammar. This is not a general theorem prover, arbitrary-code verifier, historical-novelty review or production cloud deployment.

## Testing instructions

Download the [complete test build](https://github.com/KD-code-99/noetherpilot/releases/download/v0.1.0/noetherpilot-test-build.zip), extract it, and use Python 3.12+ from the extracted folder:

```sh
python -B -m unittest discover -s tests -v
python -B -m noetherpilot serve
```

Open `http://127.0.0.1:4188` and run the labelled deterministic control. Inspect the seed's counterexample, the candidate's guarded certificate, and the downloaded receipt; then use the interface's replay action. The equivalent command-line check is:

```sh
python -B -m noetherpilot replay --receipt evidence/browser-control-receipt.json
```

The pending live route requires a server-side `NEBIUS_API_KEY` and uses `python -B -m noetherpilot run --provider nebius --rounds 2 --out evidence/live-receipt.json`. The application does not read `.env` automatically. Do not put credentials in the entry, source or chat.

## Public source, build and evidence

- [Public Apache-2.0 repository](https://github.com/KD-code-99/noetherpilot)
- [Published v0.1.0 release](https://github.com/KD-code-99/noetherpilot/releases/tag/v0.1.0) and [downloadable test build](https://github.com/KD-code-99/noetherpilot/releases/download/v0.1.0/noetherpilot-test-build.zip)
- [Retained 8-test acceptance log](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/evidence/tests.txt)
- [Actual control receipt](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/evidence/browser-control-receipt.json)
- [Paired control comparison](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/evidence/control-feedback-comparison.json)
- [Browser validation](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/evidence/browser-validation.json)
- [New-work statement](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/NEW_WORK.md) and [copied-kernel provenance](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/vendor/PROVENANCE.json)

There is no claimed public application deployment. The downloadable source/test build is the working evaluation route.

## Demo video and screenshots

The [English narrated local demo](https://github.com/KD-code-99/noetherpilot/blob/8ba48f3c560ad57f02b91946523efb7e476194e5/media/demo-narrated.mp4) is recorded and labels deterministic control execution and adjusted playback timing. It is supporting media; public video hosting for the final entry remains pending.

Lead with the seed's exact `1 -> 0` refutation, show the feedback and guarded correction, then download and replay the receipt. Keep the provider label visible. Include the research-log screenshot and the receipt/checker view. After a real provider run exists, add its actual catalog-selected model and response metadata; do not replace the control label before that evidence exists.

## Platform feedback

The adapter implements model listing, OpenAI-compatible chat completions, structured JSON handling, usage metadata and explicit HTTP failure reporting. These paths have been exercised through contract fixtures. A small reproducible JSON-proposal example and an explicit returned provenance field linking a response to catalog/version identity would help research-agent builders keep their evidence interpretable. Live onboarding, model quality, performance and billing feedback remain unmeasured.

## Submission readiness notes

- Completed locally: working control workflow, 8 acceptance tests, browser validation, receipt replay, narrated control recording, public licensed source and downloadable test build.
- Pending: authenticated NVIDIA model call through Nebius with its actual catalog and response evidence; public video hosting; live official form review; Nebius registration/eligibility confirmation and final project entry.
- Preserve the current control/live distinction until real evidence supports changing it. Recheck the actual form before entering this copy; no custom question, identifier or prize eligibility is inferred here.
