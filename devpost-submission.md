# NoetherPilot: conjecture, refute, refine

Status: draft, not ready for final submission until a real NVIDIA/Nebius run is recorded. Track: Best Apps and Agents. Public source: https://github.com/KD-code-99/noetherpilot (verify after publication). Working test build: whole source checkout/ZIP; run instructions in README.md. Public three-minute YouTube video: pending. media/demo-narrated.mp4 is a labelled software control.

## Inspiration

Mathematical research is a sequence of testable statements, failures and revisions. A model's fluent explanation cannot replace that sequence. We already had an exact checking kernel and wanted to make the counterexample part of the model's next input instead of treating verification as an afterthought.

## What it does

NoetherPilot starts with an incorrect invariant for a rational recurrence, obtains an exact counterexample, and sends the actual feedback to a proposer. A new hypothesis is independently reconstructed and checked. Failed statements remain in the research log. A surviving supported statement produces a certificate with its domain and a replayable receipt.

## NVIDIA and Nebius integration

The new adapter uses Nebius Token Factory's authenticated model catalog and chat completions endpoint. It only selects an available NVIDIA-namespace model, preferring a Nano model, and binds the selected catalog identity to the response metadata. Two rounds and 900 output tokens per request bound the default experiment. Model expressions are parsed as data; generated code is not executed.

The adapter is implemented and contract-tested, but a live run has not been made because the server has no configured Nebius key. Replace this pending statement only after actual provider evidence is captured. A deterministic proposer or injected HTTP fixture is never counted as a live NVIDIA call.

## Existing-system advantage

NOETHER-FORGE supplies exact rational arithmetic, symbolic parameter handling, domain guards and independent obligation reconstruction. The event work supplies the live-provider interface, feedback loop and observable product. The known Lyness formula is an honest control; the submission does not claim the model discovered new mathematics.

## Results

The executed control refutes `x+y`, passes a known rational invariant and replays both mathematical checks. Acceptance tests check that feedback contains the actual counterexample, unsupported model code is rejected, changed receipts fail, missing keys do not trigger a fallback, and model selection comes from the catalog. The browser records the real local loop and evidence download.

## Platform feedback

Implemented features: model listing, OpenAI-compatible chat completions, structured JSON proposal handling, usage metadata and explicit HTTP failures. The model catalog makes provider identity checkable. A useful feature would be a standard provenance field linking returned model identity to catalog/version identity and a small reproducible JSON-output example for research agents. Live performance, billing, model quality and account onboarding feedback remain unmeasured until a real run.

## AI usage and limitations

Codex assisted implementation, tests and documentation. Model output is a hypothesis; the exact kernel supplies the supported verdict. Replay checks mathematics and receipt integrity without re-running the provider or proving historical novelty. The platform and public-video gates must be complete before submission.
