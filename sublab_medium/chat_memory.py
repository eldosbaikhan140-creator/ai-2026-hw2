"""Sublab Medium — memory you choose: the compress command.

Run:  python -m sublab_medium.chat_memory               (scripted A/B comparison)
      python -m sublab_medium.chat_memory --interactive (type `compress`, `tokens`, `quit`)

A call is stateless. The Session decides what is sent on every call:
  * uncompressed: system + every turn so far
  * compressed:   system + the validated state object + turns after the compress
"""
import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from jsonschema import Draft202012Validator
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
COMPRESS = "<compress>"

POLICY = json.loads((DATA / "policy.json").read_text())
STATE_SCHEMA = json.loads((DATA / "memory_state.schema.json").read_text())
VALIDATOR = Draft202012Validator(STATE_SCHEMA)

# Deliberately NO applicant records here: everything the assistant knows about
# the applicant must come from the conversation (or from the compressed state),
# otherwise the probes would test the record, not the memory.
SYSTEM = f"""You are the assistant of a university grant office, chatting with an applicant.
Grant rule: {POLICY['rule_human']}
Required documents: transcript, id_card. Amounts: band 1 = 250,000 KZT, band 2 = 150,000 KZT.
You do not have the applicant's file in front of you: rely only on what was said
in this conversation (or in the conversation state, if one is given). If you do not
know something, say so. Answer briefly, in the language the applicant last used."""

COMPRESS_PROMPT = """Compress the conversation above into ONE JSON object with exactly these keys:
{
  "applicant_id": string or null  (only if the conversation stated it),
  "topic": string                 (what the conversation is about, one line),
  "facts": [string]               (things the APPLICANT stated: identity, documents sent or missing, income band, relatives on file, ...),
  "decisions": [string]           (answers/conclusions the office already gave, e.g. amounts, eligibility status),
  "constraints": [string]         (conditions on how/when things can happen: days they can come, deadlines, equipment problems),
  "open_questions": [string]      (questions the applicant asked that were NOT answered yet),
  "language": string              (the language(s) the applicant uses)
}
Rules: every array present (empty if nothing). Keep each item short but specific
(keep ids, names, numbers, days verbatim). Do NOT invent anything that was not said.
Do not drop a constraint or an unanswered question just because it is not about
the grant decision. Reply with the JSON object only."""


class Session:
    def __init__(self, client):
        self.client = client
        self.turns = []          # list of {"role", "content"} since the last compress
        self.state = None        # validated state dict, or None
        self.last_usage = None

    def messages(self):
        msgs = [{"role": "system", "content": SYSTEM}]
        if self.state is not None:
            msgs.append({"role": "system",
                         "content": "Conversation state so far (earlier turns were "
                                    "compressed into this):\n" +
                                    json.dumps(self.state, ensure_ascii=False)})
        return msgs + self.turns

    def _call(self, msgs, json_mode=False):
        kw = {"response_format": {"type": "json_object"}} if json_mode else {}
        r = self.client.chat.completions.create(model=MODEL, messages=msgs, **kw)
        self.last_usage = r.usage
        return r.choices[0].message.content

    def say(self, text):
        """One applicant turn. Returns (reply, prompt_tokens_sent)."""
        self.turns.append({"role": "user", "content": text})
        reply = self._call(self.messages())
        self.turns.append({"role": "assistant", "content": reply})
        return reply, self.last_usage.prompt_tokens

    def ask_once(self, text):
        """A probe: sent on top of the current context but NOT kept in it."""
        reply = self._call(self.messages() + [{"role": "user", "content": text}])
        return reply, self.last_usage.prompt_tokens

    def compress(self):
        """Summarise into a state object. Replace history only if it validates.
        Returns (ok, message, prompt_tokens_sent, raw)."""
        msgs = self.messages() + [{"role": "user", "content": COMPRESS_PROMPT}]
        raw = self._call(msgs, json_mode=True)
        sent = self.last_usage.prompt_tokens
        try:
            state = json.loads(raw)
        except json.JSONDecodeError as e:
            return False, f"summary did not parse ({e}); history kept", sent, raw
        errors = sorted(VALIDATOR.iter_errors(state), key=str)
        if errors:
            return False, ("summary failed schema: " + "; ".join(e.message for e in errors[:3])
                           + " — history kept"), sent, raw
        self.state = state
        self.turns = []
        return True, "compressed: history replaced by state", sent, raw


def check_probe(reply, expect):
    # "150 000", "150,000", "150 000" and "150000" are the same fact.
    squash = lambda s: "".join(ch for ch in s.lower() if ch not in " ,  ")
    low, flat = reply.lower(), squash(reply)
    return any(e.lower() in low or squash(e) in flat for e in expect)


def run_script(client, compress_on):
    script = json.loads((DATA / "chat_script.json").read_text())
    s = Session(client)
    calls = []            # (label, tokens_sent)
    compress_info = None
    n = 0
    for turn in script["conversation"]:
        if turn == COMPRESS:
            if compress_on:
                ok, msg, sent, raw = s.compress()
                calls.append(("compress", sent))
                compress_info = {"ok": ok, "message": msg, "raw": raw, "state": s.state}
                print(f"    [compress] {msg} (sent {sent})", file=sys.stderr)
            continue
        n += 1
        reply, sent = s.say(turn)
        calls.append((f"turn {n}", sent))
        print(f"    turn {n}: sent {sent}  -> {reply[:70]!r}", file=sys.stderr)
    probes = []
    for p in script["probes"]:
        reply, sent = s.ask_once(p["question"])
        probes.append({"id": p["id"], "tests": p["tests"], "reply": reply,
                       "retrieved": check_probe(reply, p["expect_contains"]),
                       "sent": sent})
    return calls, probes, compress_info


def scripted(client):
    print("Run A (never compressed)...", file=sys.stderr)
    a_calls, a_probes, _ = run_script(client, compress_on=False)
    print("Run B (compressed at the <compress> turn)...", file=sys.stderr)
    b_calls, b_probes, info = run_script(client, compress_on=True)

    a_map = dict(a_calls)
    print("\n### Tokens sent per call (prompt_tokens reported by the API)\n")
    print("| Call | A — never compressed | B — compressed |")
    print("|---|---|---|")
    for label, sent in b_calls:
        print(f"| {label} | {a_map.get(label, '—')} | {sent} |")
    a_tok = [t for _, t in a_calls]
    b_tok = [t for _, t in b_calls]
    b_conv = [t for l, t in b_calls if l != "compress"]
    print(f"| **peak** | {max(a_tok)} | {max(b_tok)} (conversation calls only: {max(b_conv)}) |")
    print(f"| **total for the run** | {sum(a_tok)} | {sum(b_tok)} |")

    print("\n### Probes\n")
    print("| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |")
    print("|---|---|---|---|---|---|")
    for pa, pb in zip(a_probes, b_probes):
        fmt = lambda r: r.replace("\n", " ").replace("|", "/")
        print(f"| {pa['id']} | {pa['tests']} | {'yes' if pa['retrieved'] else 'LOST'} | "
              f"{fmt(pa['reply'])} | {'yes' if pb['retrieved'] else 'LOST'} | {fmt(pb['reply'])} |")
    print(f"| **retrieved** | | {sum(p['retrieved'] for p in a_probes)}/5 | | "
          f"{sum(p['retrieved'] for p in b_probes)}/5 | |")

    print("\n### Compression result\n")
    print(info["message"] if info else "compress never ran")
    print("```json")
    print(json.dumps(info["state"], ensure_ascii=False, indent=2) if info and info["state"]
          else (info or {}).get("raw"))
    print("```")

    OUT.mkdir(exist_ok=True)
    (OUT / "medium_results.json").write_text(json.dumps(
        {"A": {"calls": a_calls, "probes": a_probes},
         "B": {"calls": b_calls, "probes": b_probes, "compress": info}},
        ensure_ascii=False, indent=2))
    print(f"\nSaved to {OUT / 'medium_results.json'}")


def interactive(client):
    s = Session(client)
    print("Grant office chat. Commands: compress | tokens | state | quit")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "quit":
            break
        if text == "tokens":
            u = s.last_usage
            print("no call yet" if u is None else
                  f"last call: sent {u.prompt_tokens}, received {u.completion_tokens}, "
                  f"total {u.total_tokens}; messages now in context: {len(s.messages())}")
            continue
        if text == "state":
            print(json.dumps(s.state, ensure_ascii=False, indent=2))
            continue
        if text == "compress":
            before = len(s.messages())
            ok, msg, sent, raw = s.compress()
            print(f"[{msg}] (compress call sent {sent} tokens; messages {before} -> {len(s.messages())})")
            if ok:
                print(json.dumps(s.state, ensure_ascii=False, indent=2))
            else:
                print("raw summary was:", raw)
            continue
        reply, sent = s.say(text)
        print(f"office> {reply}\n  (sent {sent} tokens)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interactive", action="store_true")
    args = ap.parse_args()
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set (put it in .env)")
    client = OpenAI()
    interactive(client) if args.interactive else scripted(client)


if __name__ == "__main__":
    main()
