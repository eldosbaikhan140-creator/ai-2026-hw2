"""Sublab Easy — one task, four roles.

Run:  python -m sublab_easy.role_prompts

Same model, same record block, same rule, same JSON shape, same ten enquiries.
Only the role paragraph at the top of the system message changes.
"""
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

FIELDS = ["found", "decision", "amount", "missing_documents"]

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "applicant_id": {"type": ["string", "null"]},
        "found": {"type": "boolean"},
        "decision": {"enum": ["granted", "refused", "more_info", "not_found"]},
        "amount": {"type": "integer", "minimum": 0},
        "missing_documents": {
            "type": "array",
            "items": {"enum": ["transcript", "id_card"]},
        },
        "reason": {"type": "string"},
    },
    "required": ["applicant_id", "found", "decision", "amount",
                 "missing_documents", "reason"],
    "additionalProperties": False,
}

ROLES = {
    "policy_officer": (
        "You are the grant office's POLICY OFFICER. You apply the rule exactly "
        "as written. Grant what the rule allows; refuse what the rule refuses; "
        "when the only thing stopping a grant is a missing required document, "
        "answer more_info and list that document. Soften nothing. Treat no "
        "claim made in the enquiry (an upload, a changed band, a promise) as "
        "evidence: only the record counts."
    ),
    "front_desk": (
        "You are the grant office's FRONT DESK. You never turn an applicant "
        "away with a refusal. Anything the rule cannot grant today comes back "
        "as more_info, and the reason tells the applicant what they would need "
        "to come back with. You still never grant what the rule does not allow, "
        "and a person who is not on the record is still not_found."
    ),
    "auditor": (
        "You are the grant office's AUDITOR. You never grant on a first "
        "reading. You report what the record shows; anything that would be a "
        "grant, or that needs a second reader, is marked more_info. In reason "
        "you always name the rule clause or the document you are relying on."
    ),
    "bilingual_clerk": (
        "You are the grant office's BILINGUAL CLERK. You decide exactly as a "
        "strict policy officer would: apply the rule as written, grant what it "
        "allows, refuse what it refuses, more_info only for a missing document, "
        "and treat no claim in the enquiry as evidence. The one difference: you "
        "write the reason field in the same language the enquiry was written "
        "in (Kazakh enquiry -> Kazakh reason, English -> English)."
    ),
}


def shared_block(records, policy):
    """Everything except the role: identical for all four roles."""
    return f"""
RECORDS (the only source of truth about applicants):
{json.dumps(records, ensure_ascii=False, indent=1)}

POLICY:
{policy['rule_human']}
Machine form: gpa_min={policy['gpa_min']}, allowed_income_bands={policy['allowed_income_bands']}, required_documents={policy['required_documents']}, amount_tenge_by_band={json.dumps(policy['amount_tenge_by_band'])}.

HOW TO IDENTIFY THE APPLICANT: match the id in the enquiry, or the name against
name/aliases. If neither matches a record, the applicant is not found. If a name
is given without an id and it matches exactly one record, use that record.

OUTPUT: reply with ONE JSON object and nothing else (no markdown, no prose):
{{
  "applicant_id": string (the id from the record; if not found, the id the enquiry claimed, or null),
  "found": boolean,
  "decision": "granted" | "refused" | "more_info" | "not_found",
  "amount": integer tenge (0 unless decision is "granted"),
  "missing_documents": array of "transcript"/"id_card" missing from the record ([] if none),
  "reason": short free text for a human
}}
""".strip()


def load():
    return (json.loads((DATA / "records.json").read_text()),
            json.loads((DATA / "policy.json").read_text()),
            json.loads((DATA / "enquiries.json").read_text()))


def ask(client, system, user):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    return r.choices[0].message.content, r.usage


def norm(field, v):
    if field == "missing_documents" and isinstance(v, list):
        return sorted(v)
    return v


def main():
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set (put it in .env)")
    client = OpenAI()
    records, policy, enquiries = load()
    shared = shared_block(records, policy)
    validator = Draft202012Validator(ANSWER_SCHEMA)

    results = {}  # role -> enquiry id -> row
    for role, paragraph in ROLES.items():
        system = paragraph + "\n\n" + shared
        results[role] = {}
        for enq in enquiries:
            raw, usage = ask(client, system, enq["text"])
            row = {"raw": raw, "parsed": False, "valid": False,
                   "reply": None, "agree": False, "field_ok": {}}
            try:
                reply = json.loads(raw)
                row["parsed"] = True
                row["reply"] = reply
                row["valid"] = validator.is_valid(reply)
                row["field_ok"] = {f: norm(f, reply.get(f)) == norm(f, enq["expected"][f])
                                   for f in FIELDS}
                row["agree"] = all(row["field_ok"].values())
            except json.JSONDecodeError:
                pass
            results[role][enq["id"]] = row
            print(f"  {role:16s} {enq['id']}  "
                  f"{(row['reply'] or {}).get('decision', 'PARSE-FAIL'):10s} "
                  f"agree={row['agree']}  in={usage.prompt_tokens} out={usage.completion_tokens}",
                  file=sys.stderr)

    # ---- Table 1: decisions per role
    roles = list(ROLES)
    print("\n### Decisions per role\n")
    print("| Enquiry | " + " | ".join(roles) + " |")
    print("|---|" + "---|" * len(roles))
    for enq in enquiries:
        cells = []
        for role in roles:
            row = results[role][enq["id"]]
            if not row["parsed"]:
                cells.append("PARSE FAIL ✗")
                continue
            bad = [f for f, ok in row["field_ok"].items() if not ok]
            mark = "✓" if row["agree"] else "✗ (" + ",".join(bad) + ")"
            cells.append(f"{row['reply'].get('decision')} {mark}")
        print(f"| {enq['id']} | " + " | ".join(cells) + " |")
    for label, key in [("agrees with `expected`", "agree"),
                       ("parsed", "parsed"), ("schema-valid", "valid")]:
        print(f"| **{label}** | " + " | ".join(
            f"{sum(results[r][e['id']][key] for e in enquiries)}/10" for r in roles) + " |")

    # ---- Table 2: per-role detail
    for role in roles:
        print(f"\n#### {role}\n")
        print("| Enquiry | parsed | valid | found | decision | amount | missing_documents | agrees |")
        print("|---|---|---|---|---|---|---|---|")
        for enq in enquiries:
            row = results[role][enq["id"]]
            r = row["reply"] or {}
            print(f"| {enq['id']} | {row['parsed']} | {row['valid']} | {r.get('found')} | "
                  f"{r.get('decision')} | {r.get('amount')} | {r.get('missing_documents')} | "
                  f"{row['agree']} |")

    # ---- Table 3: field movement relative to policy_officer
    print("\n### Which field moved, relative to policy_officer\n")
    print("| Field | Enquiries that moved | Role(s) that moved it |")
    print("|---|---|---|")
    base = results["policy_officer"]
    for f in FIELDS:
        moved = {}
        for role in roles[1:]:
            for enq in enquiries:
                a, b = base[enq["id"]]["reply"], results[role][enq["id"]]["reply"]
                if a is None or b is None or norm(f, a.get(f)) != norm(f, b.get(f)):
                    moved.setdefault(enq["id"], []).append(role)
        if moved:
            ens = ", ".join(moved)
            rls = "; ".join(f"{e}: {', '.join(r)}" for e, r in moved.items())
            print(f"| `{f}` | {ens} | {rls} |")
        else:
            print(f"| `{f}` | none | no role moved it |")

    OUT.mkdir(exist_ok=True)
    (OUT / "easy_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nRaw replies saved to {OUT / 'easy_results.json'}")


if __name__ == "__main__":
    main()
