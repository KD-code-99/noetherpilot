"""Nebius Token Factory integration. A control fixture is explicitly separate."""
from __future__ import annotations
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://api.tokenfactory.nebius.com/v1/"


class ProviderUnavailable(RuntimeError):
    pass


class NebiusProvider:
    name = "nebius_token_factory"
    live = True
    def __init__(self, transport=None):
        self.key = os.environ.get("NEBIUS_API_KEY", "")
        self.model = os.environ.get("NEBIUS_MODEL", "")
        self.transport = transport or self._request
        self.validated = False
        self.live = transport is None
        if not self.live:
            self.name = "provider_contract_fixture"
        if not self.key:
            raise ProviderUnavailable("NEBIUS_API_KEY is not configured. A deterministic control is not a substitute for the required NVIDIA runtime integration.")
    def _request(self, path, payload=None):
        data=None if payload is None else json.dumps(payload).encode()
        request=Request(BASE+path,data,headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json"})
        try:
            with urlopen(request,timeout=45) as response:
                raw=response.read(200000)
                return json.loads(raw)
        except HTTPError as error:
            raise ProviderUnavailable(f"Token Factory returned HTTP {error.code}; no local result was substituted.") from error
        except (URLError,TimeoutError,json.JSONDecodeError) as error:
            raise ProviderUnavailable("Token Factory request failed or returned invalid data; no local result was substituted.") from error
    def select_model(self):
        catalog=self.transport("models")
        ids=[row["id"] for row in catalog.get("data",[]) if isinstance(row,dict) and isinstance(row.get("id"),str)]
        nvidia=[m for m in ids if m.lower().startswith("nvidia/")]
        if self.model:
            if self.model not in nvidia:raise ProviderUnavailable("NEBIUS_MODEL must identify an available NVIDIA model in the actual Token Factory catalog.")
        else:
            preferred=sorted(nvidia,key=lambda m:("nano" not in m.lower(),"nemotron" not in m.lower(),m))
            if not preferred:raise ProviderUnavailable("No NVIDIA model was returned by the Token Factory catalog.")
            self.model=preferred[0]
        self.validated = True
        return self.model
    def propose(self, problem, feedback):
        if not self.validated:self.select_model()
        messages=[{"role":"system","content":"You are a mathematical proposal engine. Return one JSON object with numerator, denominator and motivation. Use exact integer polynomial expressions only; no executable code. The user fixes the recurrence and domain. State a nonconstant state-dependent rational invariant. Learn from the actual counterexample feedback. A plausible formula is not proof; a separate arithmetic kernel decides acceptance."},
                  {"role":"user","content":json.dumps({"problem":problem,"feedback":feedback,"response_schema":{"numerator":"polynomial string","denominator":"nonzero polynomial string","motivation":"why this mechanism should be conserved"}})}]
        payload={"model":self.model,"messages":messages,"temperature":0.2,"max_tokens":900,"response_format":{"type":"json_object"}}
        raw=self.transport("chat/completions",payload)
        try:
            choice=raw["choices"][0]
            text=choice["message"]["content"]
            if not isinstance(text,str) or len(text)>12000:raise ValueError("Invalid model response")
            proposal=json.loads(text)
        except (ValueError,KeyError,IndexError,TypeError) as error:
            raise ProviderUnavailable("The NVIDIA response did not contain the required JSON proposal.") from error
        if raw.get("model",self.model)!=self.model:
            raise ProviderUnavailable("The response model identity differs from the requested NVIDIA model.")
        return proposal,{"provider":self.name,"model":self.model,"response_id":raw.get("id"),"usage":raw.get("usage",{}),"live_runtime_call":self.live}


class ControlProvider:
    """A reproducible test proposer, never described as an NVIDIA model."""
    name = "deterministic_control"
    live = False
    def propose(self, problem, feedback):
        return {"numerator":"(x+1)*(y+1)*(x+y+a)","denominator":"x*y","motivation":"Known Lyness control: test the standard rational invariant after exact refutation of x+y."}, {"provider":self.name,"model":None,"live_runtime_call":False}
