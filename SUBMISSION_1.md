# HW2 submission

**Name:** Baikhan Yeldos
**Student ID:** S23068842
**Group:** GSS4007-eng-8
**Repository:** https://github.com/eldosbaikhan140-creator/ai-2026-hw2

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not. If you used a model to help you draft a prompt, say which prompt.

> Claude (Anthropic) wrote the code for all three programs, including the system
> prompts (the four role paragraphs in Sublab Easy, the compress prompt in Sublab
> Medium, the extraction and scoring prompts in Sublab Hard). After my first run
> of Sublab Hard failed schema validation, Claude changed the extraction call to
> OpenAI strict structured outputs. Claude also copied the tables my programs
> printed into this file. I ran all three programs myself with my own key; every
> number below is from my own run. I wrote the written answers myself in Russian;
> Claude explained the questions to me beforehand and translated my answers into
> English.

---

## Sublab Easy — one task, four roles

### Decisions per role

One row per enquiry. In each cell write the `decision` your run returned, and
whether it agrees with `expected` in `data/enquiries.json`:

| Enquiry | policy_officer | front_desk | auditor | bilingual_clerk |
|---|---|---|---|---|
| E-01 | granted ✓ | granted ✓ | more_info ✗ (decision, amount) | granted ✓ |
| E-02 | more_info ✓ | more_info ✓ | more_info ✓ | more_info ✓ |
| E-03 | refused ✓ | more_info ✗ (decision) | refused ✓ | refused ✓ |
| E-04 | refused ✓ | more_info ✗ (decision) | refused ✓ | refused ✓ |
| E-05 | granted ✓ | granted ✓ | more_info ✗ (decision, amount) | granted ✓ |
| E-06 | granted ✓ | granted ✓ | more_info ✗ (decision, amount) | granted ✓ |
| E-07 | granted ✓ | granted ✓ | more_info ✗ (decision, amount) | granted ✓ |
| E-08 | not_found ✓ | not_found ✓ | not_found ✓ | not_found ✓ |
| E-09 | refused ✓ | more_info ✗ (decision) | refused ✓ | refused ✓ |
| E-10 | more_info ✓ | more_info ✓ | more_info ✓ | more_info ✓ |
| **agrees with `expected`** | 10/10 | 7/10 | 6/10 | 10/10 |
| **parsed** | 10/10 | 10/10 | 10/10 | 10/10 |
| **schema-valid** | 10/10 | 10/10 | 10/10 | 10/10 |

### The four role tables (all four checked fields)

#### policy_officer

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | ✓ |
| E-02 | true | more_info | 0 | [id_card] | ✓ |
| E-03 | true | refused | 0 | [] | ✓ |
| E-04 | true | refused | 0 | [] | ✓ |
| E-05 | true | granted | 250000 | [] | ✓ |
| E-06 | true | granted | 150000 | [] | ✓ |
| E-07 | true | granted | 250000 | [] | ✓ |
| E-08 | false | not_found | 0 | [] | ✓ |
| E-09 | true | refused | 0 | [] | ✓ |
| E-10 | true | more_info | 0 | [id_card] | ✓ |

#### front_desk

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | ✓ |
| E-02 | true | more_info | 0 | [id_card] | ✓ |
| E-03 | true | more_info | 0 | [] | ✗ |
| E-04 | true | more_info | 0 | [] | ✗ |
| E-05 | true | granted | 250000 | [] | ✓ |
| E-06 | true | granted | 150000 | [] | ✓ |
| E-07 | true | granted | 250000 | [] | ✓ |
| E-08 | false | not_found | 0 | [] | ✓ |
| E-09 | true | more_info | 0 | [] | ✗ |
| E-10 | true | more_info | 0 | [id_card] | ✓ |

#### auditor

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | more_info | 0 | [] | ✗ |
| E-02 | true | more_info | 0 | [id_card] | ✓ |
| E-03 | true | refused | 0 | [] | ✓ |
| E-04 | true | refused | 0 | [] | ✓ |
| E-05 | true | more_info | 0 | [] | ✗ |
| E-06 | true | more_info | 0 | [] | ✗ |
| E-07 | true | more_info | 0 | [] | ✗ |
| E-08 | false | not_found | 0 | [] | ✓ |
| E-09 | true | refused | 0 | [] | ✓ |
| E-10 | true | more_info | 0 | [id_card] | ✓ |

#### bilingual_clerk

| Enquiry | found | decision | amount | missing_documents | agrees |
|---|---|---|---|---|---|
| E-01 | true | granted | 250000 | [] | ✓ |
| E-02 | true | more_info | 0 | [id_card] | ✓ |
| E-03 | true | refused | 0 | [] | ✓ |
| E-04 | true | refused | 0 | [] | ✓ |
| E-05 | true | granted | 250000 | [] | ✓ |
| E-06 | true | granted | 150000 | [] | ✓ |
| E-07 | true | granted | 250000 | [] | ✓ |
| E-08 | false | not_found | 0 | [] | ✓ |
| E-09 | true | refused | 0 | [] | ✓ |
| E-10 | true | more_info | 0 | [id_card] | ✓ |

### Which field moved, on which enquiry, under which role

| Field | Enquiries that moved | Role(s) that moved it |
|---|---|---|
| `found` | none | no role moved it |
| `decision` | E-03, E-04, E-09 · E-01, E-05, E-06, E-07 | front_desk on E-03, E-04, E-09 (refused → more_info); auditor on E-01, E-05, E-06, E-07 (granted → more_info) |
| `amount` | E-01, E-05, E-06, E-07 | auditor (250000 / 150000 → 0, a consequence of not granting) |
| `missing_documents` | none | no role moved it |

Fields that moved on no enquiry: `found` and `missing_documents`.
bilingual_clerk moved no structured field on any enquiry (10/10 identical to policy_officer).

### Raw replies

Paste the full reply for **one enquiry where a role changed the decision** away
from the policy officer's:

```
front_desk, E-03 (policy_officer said refused):
{
  "applicant_id": "A-203",
  "found": true,
  "decision": "more_info",
  "amount": 0,
  "missing_documents": [],
  "reason": "The record shows a GPA of 2.4, below the required 2.67. Provide an updated transcript showing a GPA of at least 2.67 for reconsideration."
}
```

Paste the full reply for **E-07 (the Kazakh enquiry)** from the bilingual
clerk, so the `reason` language is visible:

```
{
  "applicant_id": "A-201",
  "found": true,
  "decision": "granted",
  "amount": 250000,
  "missing_documents": [],
  "reason": "Сіз грант талаптарына сай келесіз: GPA 2.67-ден жоғары, табыс санаты 1 және қажетті құжаттардың екеуі де бар."
}
```

### Written answers

**1. Which fields are role-sensitive and which are not?** Point at rows in your
tables.

> `found` and `missing_documents` are not role-sensitive: neither field moved on any enquiry under any role, because both come straight from the applicant's record.
>
> `decision` is the most role-sensitive field. Under `front_desk` it moved on E-03, E-04 and E-09, because this role avoids a direct refusal and returns `more_info` instead. Under `auditor` it moved on E-01, E-05, E-06 and E-07, because this role must not grant on a first reading.
>
> `amount` also moved under `auditor`, but only as a consequence of `decision`: if no grant is given, the amount becomes 0.
>
> `bilingual_clerk` did not move any of the checked structured fields and scored 10/10. Its role only changes the `reason` text, which is written in the language of the enquiry. So from my counts: front_desk and auditor move `decision`; bilingual_clerk moves only `reason`.

**2. Which enquiries are most sensitive to the role, and why those?** Say what
E-03, E-04, E-07 and E-10 are each testing.

> The most sensitive enquiries are the ones where the roles are supposed to treat the final decision differently.
>
> E-03 and E-04 test cases where the policy officer must refuse because the applicant does not meet the rule (GPA in E-03, income band in E-04). `front_desk` replaced the refusal with `more_info` in both, because this role must not refuse the applicant directly.
>
> E-07 is interesting because the enquiry is in Kazakh. It tests whether the language of the enquiry changes the decision itself. The result shows it does not: under `bilingual_clerk` only the language of `reason` changed, the decision stayed `granted`.
>
> E-10 tests whether the model trusts the applicant's claim that the document was already uploaded. The record does not confirm it, so every role relied on the record rather than the claim and returned `more_info` with `id_card` missing.

**3. Where does discretion belong — the role paragraph, or code that reads
`decision` afterwards?** Say what a downstream program can and cannot tell
about which role produced a record.

> I think the important decision logic belongs in code, not only in the role prompt.
>
> For example, if a downstream program receives a JSON record with `decision: "more_info"`, it cannot tell why that decision was made or which role produced it. The JSON contains no information about the role. So any difference in behaviour that exists only inside the prompt becomes invisible to the next part of the program.
>
> A role prompt can be used to change the model's behaviour or style, but if a difference affects an important decision, it should be implemented, or at least checked again, in code. Then the behaviour is explicit, predictable and testable.

**4. Is a role a boundary?** Say in Week 2 terms what the role paragraph is
made of, and what you would put in code — not in the prompt — if a wrong
`decision` were expensive.

> No, a role by itself is not a reliable security boundary. The role paragraph is just text tokens passed to the model together with the rest of the context. The model generates a continuation of the whole context, so a text instruction is not as strict a constraint as a check in a program.
>
> If a wrong decision could have serious consequences, the core rules should be checked in code. For example, the program can check GPA, income band and the required documents itself, and then compare that result with the `decision` the model returned. That way the model helps interpret the enquiry, but the critical constraint is enforced by code.

---

## Sublab Medium — memory you choose

### Tokens per call

`prompt_tokens` as reported by the API. The `<compress>` turn is skipped in run A;
in run B it is the extra compress call.

| Call | A — never compressed | B — compressed at the `compress` turn |
|---|---|---|
| 1 (turn 1) | 230 | 230 |
| 2 (turn 2) | 321 | 306 |
| 3 (turn 3) | 379 | 361 |
| 4 (turn 4) | 439 | 417 |
| 5 (turn 5) | 499 | 465 |
| 6 (turn 6) | 555 | 517 |
| 7 (turn 7) | 641 | 573 |
| 8 (turn 8) | 700 | 646 |
| 9 (turn 9) | 789 | 695 |
| 10 (compress) | — (skipped) | 971 |
| 11 (turn 10) | 864 | 568 |
| 12 (turn 11) | 954 | 669 |
| **peak** | 954 | 971 (the compress call); 695 among conversation calls |
| **total for the run** | 6371 | 6418 |

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 identity | turn 1 | yes | You are **Daniyar Qoshan**, applicant **A-202**. | yes | You are **Daniyar Qoshan**, applicant number **A-202**. |
| Q-2 missing document | turn 5 | yes | The **id_card** is still missing or unconfirmed. Your transcript was mentioned as sent, but its presence on file is not verified. | yes | The **ID card** is still missing from your file. Your transcript has been reported as sent, but it has not yet been verified as on file. |
| Q-3 band and amount | turns 3–4 | yes | Your income band is not verified in the record. If it is confirmed as **band 2**, the grant amount would be **150,000 KZT**. | yes | You stated that your income band is **2**, but it has not been verified in the record. If confirmed and you meet all other requirements, the amount would be **150,000 KZT**. |
| Q-4 the constraint | turn 6 | yes | You said you can come to the office on **Thursday**. | yes | You can come to the office on **Thursdays**. |
| Q-5 the open question | turn 7 | yes | You asked whether a scanned letter from your employer would count, or whether the original was required. I said the record doesn't specify this and advised confirming with the grant office. | yes | You asked whether a **scanned employer letter** would be accepted or whether the **original** is required. The record does not specify the answer. |
| **retrieved** | | 5/5 | | 5/5 | |

### The state my compression produced

Validated against `data/memory_state.schema.json`: valid, so the turns were replaced by it.

```json
{
  "applicant_id": "A-202",
  "topic": "Study grant eligibility, required documents, grant amount, and application processing",
  "facts": [
    "Applicant is Daniyar Qoshan.",
    "Applicant stated they sent their transcript last week.",
    "Applicant stated their income band is 2 based on a family certificate.",
    "Applicant could not upload the ID card because the home scanner broke.",
    "Applicant can come to the office only on Thursdays due to labs during the week.",
    "Applicant stated their sister Aruzhan applied last year and is on file."
  ],
  "decisions": [
    "Eligibility could not be determined because GPA, income band, transcript, and ID card were not verified.",
    "If approved with verified income band 2, the grant amount would be 150,000 KZT.",
    "The ID card was not verified as on file, so the documented requirements were not currently met.",
    "The ID card may be submitted on Thursday; eligibility cannot be confirmed until it is verified and on file.",
    "The record does not specify whether a scanned employer letter is acceptable.",
    "The record does not specify how quickly decisions are made after ID card submission.",
    "Aruzhan's record could not be verified and does not establish A-202's eligibility."
  ],
  "constraints": [
    "The home scanner is broken.",
    "Applicant can visit the office only on Thursdays.",
    "Applicant has lab all week otherwise."
  ],
  "open_questions": [
    "Whether a scanned employer letter counts or the original is required.",
    "Whether the decision will be made the same day if the ID card is brought on Thursday."
  ],
  "language": "Kazakh and English"
}
```

### Written answers

**1. What did compression buy?** Peak tokens both ways, probes retrieved both
ways, and — if a probe was lost — which one and which turn it came from.

> Without compression the peak was 954 tokens sent. With compression the overall peak was slightly higher, 971 tokens, because the compress call itself has to send the whole conversation plus the instruction. After compression, however, the normal calls became noticeably smaller: 568 and 669 tokens instead of 864 and 954.
>
> Memory quality did not get worse in this run. In both modes the program answered 5/5 probes correctly, so no tested fact was lost after compression.
>
> For this short conversation compression did not save tokens overall: 6418 in total versus 6371 without it. This shows compression has an up-front cost and only pays off in longer conversations, where the smaller state is re-sent many times.

**2. Why must the state be structured rather than a paragraph?** You could have
asked for "a summary". Say what changes when the summary is an object with
named fields.

> A structured state is more useful than a plain-text summary because every value sits in a named field. Such an object can be validated automatically against `memory_state.schema.json`.
>
> The structure also forces the model to keep important categories separately, such as `constraints` and `open_questions`. In my run this is why details like Thursday and the open question about the employer letter survived.
>
> A program can also read the field it needs directly. If the memory were a single paragraph, the program would have to extract the information from unstructured text again, which adds another source of errors.

**3. What is missing from your state that you would add?** Name what you would
add and what you would drop to pay for it.

> I would add a clearer separation between information that is confirmed and information the applicant only claimed. For example, documents actually present in the record could be stored separately from documents the applicant says they sent.
>
> It would also be useful to keep important numeric values in their own fields, for example the income band or the grant amount, instead of leaving them inside free text.
>
> To keep the state from growing too large, I would shorten the `decisions` field in exchange, since it repeats information already stored in other fields. That keeps the memory compact but more useful for later checks in code.

**4. When is compression the wrong choice?** Name a conversation where it would
lose something that cannot be recovered, and say whether your program would
notice.

> Compression is a bad choice when the exact original wording matters, for example a legal consent, precise numbers, a verbatim quote, or the text of an official complaint.
>
> After compression the original messages are replaced by the summary. If the model paraphrases or leaves out an important detail, the original text cannot be recovered from the compressed state.
>
> My program might not even notice such a loss. Validation checks that the object matches the schema, but it does not guarantee that the summary kept every important detail of the original conversation.

---

## Sublab Hard — stories in, CVs out, the best candidate by code

### Part 1 — extraction

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |
|---|---|---|---|---|
| story-01 | yes | yes | — | none of the four (1 unpublished item and 1 ambiguity note recorded) |
| story-02 | yes | yes | gpa_original, gpa_original_scale, gpa_4_scale | **no GPA stated** → null, not inferred from "diploma with distinction" |
| story-03 | yes | yes | — | **GPA on another scale**: 4.6 / 5.0 → 3.68 on 4.0, scale 5.0 recorded; **unpublished paper** (under review) listed, not counted |
| story-04 | yes | yes | — | **unpublished papers**: 1 under review + 2 in preparation listed separately, not counted → 1 published |
| story-05 | yes | yes | — | **unpublished paper** (written, not submitted) not counted; story in Kazakh |
| story-06 | yes | yes | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | **contradiction**: GPA 3.2 vs 3.5 → null; graduated 2024 vs graduating 2026 → null; both recorded in `ambiguities` |

(First run, before the fix: all six parsed but 0/6 validated. The model invented its
own shapes for nested fields, e.g. languages as `{"language": ..., "proficiency": ...}`
objects instead of strings. After switching to strict structured outputs: 6/6 valid.)

The four traps, for reference: no GPA stated · a GPA on another scale · a paper
that is not published · a story that contradicts itself.

Paste the extraction for **story-06**, the one that contradicts itself:

```json
{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "story_language": "English",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_original": null,
  "gpa_original_scale": null,
  "gpa_4_scale": null,
  "languages": ["Kazakh", "Russian", "English"],
  "published_peer_reviewed_count": 1,
  "published_outputs": [
    "Paper on survey weighting, published in peer-reviewed proceedings"
  ],
  "unpublished_outputs": [
    {"title_or_topic": "Poster at a local event", "status": "not counted as a publication"}
  ],
  "experience_periods": [
    {"role": "Insurance analytics team", "start": "February 2023", "end": null, "months": 40, "countable": true}
  ],
  "experience_months_countable": 40,
  "ambiguities": [
    "graduation_year: story says graduated in 2024 and is currently a final-year student graduating in 2026 ('I graduated in 2024 with a BSc in Statistics.' and 'I am currently a final-year student graduating in 2026')",
    "gpa: story says 3.2 and then 3.5 ('My GPA was 3.2. Actually I should double-check that, I think it was 3.5')",
    "experience: the 40 months include eight months of part-time work ('I was part-time for the first eight of those while I was still studying, then full-time.')"
  ],
  "evidence": {
    "full_name": "# Nurzhan Abilov",
    "degree": "I graduated in 2024 with a BSc in Statistics.",
    "graduation_year": null,
    "gpa": null,
    "languages": "Languages: Kazakh, Russian, English.",
    "publications": "one paper published, in a peer-reviewed proceedings, on survey weighting. One poster at a local event, which I do not think counts.",
    "experience": "I have been at an insurance analytics team since February 2023, which is about forty months."
  }
}
```

### Part 2 — scores and the winner

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|---|---|---|---|
| story-01 | 5 | 5 | 2 | 4.40 |
| story-02 | 0 | 0 | 5 | 1.00 |
| story-03 | 4 | 3 | 3 | 3.50 |
| story-04 | 4 | 3 | 5 | 3.90 |
| story-05 | 5 | 3 | 2 | 3.80 |
| story-06 | 1 | 3 | 5 | 2.40 |

Weighted total = 0.5 · academic + 0.3 · research + 0.2 · experience, computed in Python.
Ranking (code): story-01 (4.40) > story-04 (3.90) > story-05 (3.80) > story-03 (3.50) > story-06 (2.40) > story-02 (1.00)

Model's one-line notes per score (from the scoring call):
- story-01: GPA is 3.8/4.0 with two published peer-reviewed outputs and 8 countable experience months.
- story-02: No GPA is stated, the publication is not confirmed peer-reviewed, and 36 experience months are countable.
- story-03: The 4.6/5.0 GPA converts to 3.68/4.0, with one published output and 14 experience months.
- story-04: GPA is 3.6/4.0, with one published output and 24 countable experience months.
- story-05: GPA is 3.9/4.0, with one published output and 6 countable experience months.
- story-06: The GPA is contradictory, so academic scoring relies only on the stated degree; there is one publication and 40 countable experience months.

**Winner, computed by my code:** story-01 (Aziza Bekova), 4.40. Margin over story-04: 0.50.

**The model's prose answer, asked separately ("who should win?"):**

> Aziza Bekova should win: she has a strong 3.8/4.0 GPA, the only two qualifying
> peer-reviewed publications, and eight months of relevant experience. Using scores
> **(academic, research, experience)** and the prescribed weights, the ranking is:
>
> 1. **Aziza Bekova** — (5, 5, 2) — **4.60**
> 2. **Tamerlan Saparov** — (4, 2, 5) — **3.60**
> 3. **Lyazzat Omarova** — (4, 2, 3) — **3.20**
> 4. **Aisha Nurlankyzy** — (5, 2, 1) — **3.10**
> 5. **Dias Yerzhanov** — (0, 2, 5) — **1.60**
> 6. **Nurzhan Abilov** — academic score **null** because the story contradicts itself
>    about the GPA; he has one published paper and 40 months' experience, but his
>    total cannot validly be computed without resolving that contradiction.

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

> In my first extraction run none of the six records passed validation. The model chose its own data format, for example it returned languages as objects instead of plain strings.
>
> So I had to make the response format stricter and use structured outputs with a schema, so that the model returns the fields in a predefined format.
>
> A separate problem came from contradictions. For story-06 I had to state explicitly how a contradiction should be recorded (as a string in `ambiguities`), because without a strict rule the output could fail validation. This showed that it is not enough to ask the model to "extract the data": the format and the handling of ambiguous cases must be defined explicitly.

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

> An example of the model guessing is story-02. The story uses the word "published", but the model gave a research score of 0 because it decided the text did not sufficiently confirm the publication was peer-reviewed. That decision came from the model's own interpretation of the text.
>
> The code, on the other hand, was responsible for calculating the weighted total and choosing the winner. The model returned only the per-criterion scores, and the total was computed by the program.
>
> This split matters because the model interprets unstructured text, while exact arithmetic and comparing numbers can be done reliably in code.

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

> Yes, both picked the same winner, Aziza (story-01). But there were important differences.
>
> In the prose ranking the model stated a total of 4.60 for her, although applying the given weights to its own scores (5, 5, 2) gives 4.40. Some individual scores also differed: for example, the research scores for Tamerlan, Lyazzat and Aisha were 2 in the prose answer and 3 in the scoring call.
>
> So I trust the computed ranking more. It can be reproduced and checked: the criteria arrive as separate numeric fields, and the weighted total is calculated by one known formula in code. The prose ranking can look convincing, but the 4.60 example shows the model can make an arithmetic mistake even when its explanation sounds logical.

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

> In my run, when the GPA values contradicted each other, `gpa_4_scale` became `null` and the contradiction was recorded separately. During scoring the model gave an academic score of 1 instead of 0, because other academic information, such as the degree, was still present.
>
> I would not automatically choose one of the contradicting values, because that would mean inventing a rule that is not in the rubric. A more reliable option is to keep the GPA as `null`, flag the contradiction explicitly, and send the case to a human for review.
>
> A future version of the rubric should include a separate rule for contradicted fields, so that identical cases are always handled the same way.

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

> In my computed ranking the top two candidates scored 4.40 and 3.90. The gap is 0.50, which is much larger than the 0.05 threshold.
>
> If the gap had been below 0.05, I would not present the result to the committee as clear-cut. I would say the candidates are practically equal under the current rubric, and I would re-check the extraction for both of them, especially the evidence quotes, the GPA conversion, and the counts of publications and months of experience.
>
> After that I would recompute the scores. With such a small gap, even a small extraction error or an ambiguous reading of one fact could change the order of the candidates.

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

>
