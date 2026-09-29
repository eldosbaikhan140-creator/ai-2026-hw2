"""Sublab Hard — stories in, CVs out, the best candidate by code.

Run:  python -m sublab_hard.cv_extract_and_rank

1. extract a CV (JSON, validated) from each story
2. ask the model for three 0-5 scores per candidate — nothing else
3. compute the weighted total and the winner in Python
4. separately, ask the model in prose who should win
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
RUBRIC = json.loads((DATA / "candidate_rubric.json").read_text())
WEIGHTS = {c["id"]: c["weight"] for c in RUBRIC["criteria"]}

NUM_OR_NULL = {"type": ["number", "null"]}
INT_OR_NULL = {"type": ["integer", "null"]}
STR_OR_NULL = {"type": ["string", "null"]}
STR_LIST = {"type": "array", "items": {"type": "string"}}


def obj(props):
    """Strict-mode object: every key required, nothing extra allowed."""
    return {"type": "object", "properties": props,
            "required": list(props), "additionalProperties": False}


EVIDENCE_FIELDS = ["full_name", "degree", "graduation_year", "gpa",
                   "languages", "publications", "experience"]

CV_SCHEMA = obj({
    "candidate_id": {"type": "string"},
    "full_name": STR_OR_NULL,
    "story_language": {"type": "string"},
    "degree": STR_OR_NULL,
    "graduation_year": INT_OR_NULL,
    "gpa_original": NUM_OR_NULL,
    "gpa_original_scale": NUM_OR_NULL,
    "gpa_4_scale": NUM_OR_NULL,
    "languages": STR_LIST,
    "published_peer_reviewed_count": INT_OR_NULL,
    "published_outputs": STR_LIST,
    "unpublished_outputs": {"type": "array", "items": obj({
        "title_or_topic": {"type": "string"}, "status": {"type": "string"}})},
    "experience_periods": {"type": "array", "items": obj({
        "role": {"type": "string"}, "start": STR_OR_NULL, "end": STR_OR_NULL,
        "months": INT_OR_NULL, "countable": {"type": "boolean"}})},
    "experience_months_countable": INT_OR_NULL,
    "ambiguities": STR_LIST,
    "evidence": obj({f: STR_OR_NULL for f in EVIDENCE_FIELDS}),
})
CV_VALIDATOR = Draft202012Validator(CV_SCHEMA)

EXTRACT_SYSTEM = f"""You turn a scholarship applicant's free-text story into ONE JSON record.
You are a careful clerk, not an evaluator: copy what the story states, nothing more.

RULES (follow all of them):
1. NULL, NEVER ESTIMATE. A fact the story does not state is null. No GPA stated
   means gpa_original, gpa_original_scale and gpa_4_scale are all null — do not
   infer a GPA from "distinction", the degree, the university or the tone.
2. GPA SCALE. Record gpa_original and gpa_original_scale exactly as written.
   gpa_4_scale = gpa_original / gpa_original_scale * 4.0, rounded to 2 decimals
   (if the scale is already 4.0, copy the number). If the story does not state
   the scale, gpa_original_scale is null and gpa_4_scale is null.
3. PUBLISHED MEANS PUBLISHED. A paper counts in published_peer_reviewed_count
   only if the story says it is published or accepted AND peer-reviewed (or in
   peer-reviewed proceedings/journal). Submitted, under review, in preparation,
   planned, in press, posters and talks are NOT published: list them in
   unpublished_outputs with their status and do not count them.
4. CONTRADICTIONS ARE NOT RESOLVED. If the story gives two incompatible values
   for a field (two GPAs, two graduation years, finished and not finished),
   that field is null, and an entry in "ambiguities" states both values and
   the quote. Do not pick one, do not average. Each ambiguities item is ONE
   STRING, e.g. "gpa: story says 3.2 and then 3.5 ('My GPA was 3.2. ... I think it was 3.5')".
5. EXPERIENCE IN MONTHS. List every period in experience_periods. months is the
   stated or date-computable length; a period with no stated months and no
   dates has months=null and countable=false. Overlapping periods count once.
   experience_months_countable = sum of countable months (null if none can be
   counted). Count all countable work the story gives, relevant or not, and
   note in ambiguities if its relevance is doubtful or part-time.
6. EVIDENCE. For every non-null field, evidence[field] is a short verbatim
   quote from the story (in the story's own language), as a string.
   Null field -> null.
7. The story may be in Kazakh, Russian or English. Field values in English;
   quotes verbatim.
8. graduation_year is the year the degree was / will be completed, as an integer.

Output shape (enforced by a JSON schema): languages is a list of plain strings
like "English (C1)"; published_outputs is a list of plain strings (one short
description each); unpublished_outputs items are {{"title_or_topic", "status"}};
experience_periods items are {{"role", "start", "end", "months", "countable"}};
ambiguities is a list of plain strings; evidence has one verbatim quote (or null)
for each of: {", ".join(EVIDENCE_FIELDS)}. candidate_id = the id given to you."""

SCORE_SCHEMA = {
    "type": "object",
    "properties": {"scores": {"type": "array", "items": {
        "type": "object",
        "properties": {"candidate_id": {"type": "string"},
                       "academic": {"type": "integer", "minimum": 0, "maximum": 5},
                       "research": {"type": "integer", "minimum": 0, "maximum": 5},
                       "experience": {"type": "integer", "minimum": 0, "maximum": 5},
                       "note": {"type": "string"}},
        "required": ["candidate_id", "academic", "research", "experience"],
        "additionalProperties": False}}},
    "required": ["scores"],
}
SCORE_VALIDATOR = Draft202012Validator(SCORE_SCHEMA)

SCORE_SYSTEM = f"""You score scholarship candidates against a fixed rubric.
Rubric (verbatim): {json.dumps(RUBRIC['criteria'], ensure_ascii=False)}
Counting rules (verbatim): {json.dumps(RUBRIC['counting_rules'], ensure_ascii=False)}

Additional rules:
- Score from the extracted records you are given. Use the counted fields
  (gpa_4_scale, published_peer_reviewed_count, experience_months_countable);
  do not re-count or re-interpret the stories.
- A field that is null because of a contradiction: score from what is NOT
  contradicted (e.g. degree stated but GPA contradicted -> academic is low but
  not 0, since academic information exists); say so in note.
- A field that is null because it was never stated: score as if absent.
- Each score is an integer 0-5. Do NOT compute a weighted total, a rank or a
  winner. That is done elsewhere.

Reply with JSON only: {{"scores": [{{"candidate_id": "...", "academic": int,
"research": int, "experience": int, "note": "one short sentence"}}, ...]}}"""


def call_json(client, system, user, schema=None, name="reply"):
    """JSON mode; with a schema, OpenAI strict structured outputs."""
    fmt = ({"type": "json_schema",
            "json_schema": {"name": name, "strict": True, "schema": schema}}
           if schema else {"type": "json_object"})
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        response_format=fmt)
    return r.choices[0].message.content


def traps(cv):
    """Which of the four traps this extraction ran into (what it recorded)."""
    hit = []
    amb_text = json.dumps(cv.get("ambiguities", []), ensure_ascii=False).lower()
    if cv.get("gpa_original") is None and "gpa" not in amb_text:
        hit.append("no GPA stated -> null")
    if cv.get("gpa_original_scale") not in (None, 4, 4.0):
        hit.append(f"GPA on {cv['gpa_original_scale']} scale -> {cv.get('gpa_4_scale')}")
    if cv.get("unpublished_outputs"):
        hit.append(f"{len(cv['unpublished_outputs'])} unpublished output(s) not counted")
    if cv.get("ambiguities"):
        hit.append(f"{len(cv['ambiguities'])} ambiguity/contradiction recorded")
    return hit


def main():
    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set (put it in .env)")
    client = OpenAI()
    OUT.mkdir(exist_ok=True)

    # ---------- Part 1: extraction
    cvs, rows = {}, []
    for path in sorted((DATA / "candidates").glob("story-*.md")):
        cid = path.stem
        raw = call_json(client, EXTRACT_SYSTEM,
                        f"candidate_id: {cid}\n\nSTORY:\n{path.read_text()}",
                        schema=CV_SCHEMA, name="cv")
        parsed, valid, errs, cv = False, False, [], None
        try:
            cv = json.loads(raw)
            parsed = True
            errs = [f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}"
                    for e in CV_VALIDATOR.iter_errors(cv)]
            valid = not errs
        except json.JSONDecodeError as e:
            errs = [str(e)]
        cvs[cid] = cv if cv is not None else {"candidate_id": cid, "raw": raw}
        nulls = [k for k in CV_SCHEMA["required"] if cv is not None and cv.get(k) is None]
        rows.append((cid, parsed, valid, nulls, traps(cv) if cv else [], errs))
        print(f"  extracted {cid}: parsed={parsed} valid={valid}"
              + ("" if valid else f"  errors: {errs[:3]}"), file=sys.stderr)
    (OUT / "hard_cvs.json").write_text(json.dumps(cvs, ensure_ascii=False, indent=2))

    print("\n### Part 1 — extraction\n")
    print("| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |")
    print("|---|---|---|---|---|")
    for cid, p, v, nulls, t, errs in rows:
        vv = "yes" if v else "NO: " + "; ".join(errs[:2])
        print(f"| {cid} | {'yes' if p else 'NO'} | {vv} | {', '.join(nulls) or '—'} | {'; '.join(t) or '—'} |")
    print("\nstory-06 extraction:\n```json")
    print(json.dumps(cvs.get("story-06"), ensure_ascii=False, indent=2))
    print("```")

    # ---------- Part 2: scores from the model, total and winner from code
    raw = call_json(client, SCORE_SYSTEM,
                    "Extracted records:\n" + json.dumps(list(cvs.values()), ensure_ascii=False, indent=1))
    scores_obj = json.loads(raw)
    errs = [e.message for e in SCORE_VALIDATOR.iter_errors(scores_obj)]
    if errs:
        sys.exit("score reply failed schema: " + "; ".join(errs) + "\n" + raw)
    scores = {s["candidate_id"]: s for s in scores_obj["scores"]}
    missing = set(cvs) - set(scores)
    if missing:
        sys.exit(f"model returned no scores for {sorted(missing)}")

    totals = {cid: round(sum(WEIGHTS[k] * scores[cid][k] for k in WEIGHTS), 2)
              for cid in cvs}
    ranking = sorted(totals, key=lambda c: -totals[c])
    top = totals[ranking[0]]
    winners = [c for c in ranking if totals[c] == top]

    print("\n### Part 2 — scores (model) and weighted total (code)\n")
    print("| Candidate | academic | research | experience | weighted total (code) | model note |")
    print("|---|---|---|---|---|---|")
    for cid in sorted(cvs):
        s = scores[cid]
        print(f"| {cid} | {s['academic']} | {s['research']} | {s['experience']} | "
              f"{totals[cid]:.2f} | {s.get('note', '')} |")
    print("\nRanking (code): " + " > ".join(f"{c} ({totals[c]:.2f})" for c in ranking))
    if len(winners) > 1:
        print(f"**Winner, computed by code: TIE between {', '.join(winners)} at {top:.2f}** — "
              "the rubric does not break ties; refer to the committee.")
    else:
        gap = top - totals[ranking[1]]
        print(f"**Winner, computed by code: {ranking[0]} with {top:.2f}** "
              f"(margin over {ranking[1]}: {gap:.2f}{' — within 0.05, flag to committee' if gap <= 0.05 else ''})")

    # ---------- Part 2b: prose answer, separate call, no scores shown
    stories = "\n\n".join(f"=== {p.stem}\n{p.read_text()}"
                          for p in sorted((DATA / "candidates").glob("story-*.md")))
    r = client.chat.completions.create(model=MODEL, messages=[
        {"role": "system", "content": "You advise a scholarship committee. Rubric: "
         + json.dumps(RUBRIC, ensure_ascii=False)},
        {"role": "user", "content": "Here are the six applications. Which candidate should "
         "win the one funded place, and why? Answer in a short paragraph and give your "
         "full ranking.\n\n" + stories}])
    prose = r.choices[0].message.content
    print("\n### The model's prose answer (separate call)\n")
    print(prose)

    (OUT / "hard_results.json").write_text(json.dumps(
        {"cvs": cvs, "scores": scores, "totals": totals, "ranking": ranking,
         "prose": prose}, ensure_ascii=False, indent=2))
    print(f"\nSaved to {OUT / 'hard_results.json'}")


if __name__ == "__main__":
    main()
