# Acadza Product Note — Protecting Question Integrity

**Audience:** Acadza Product and Engineering  
**Scope:** The supplied 43-question / 44-report assignment fixture

## Who loses most when a question is broken?

The highest cost falls on a diligent JEE/NEET student who has learned the concept correctly but is marked wrong by a bad key or misleading solution. They lose marks, study time and confidence—and every later student who encounters the same question can be affected too.

That is why the workflow treats a student report as a useful signal, not proof. It checks the report against the question, stored answer and solution; groups reports by question; prioritises repeated and high-impact cases; and gives faculty the evidence and a minimal before/after patch instead of asking them to reconstruct the issue from scratch. Replies should explain a no-error decision respectfully, without making the student feel foolish.

## What I would never let an LLM auto-apply

I would never allow an LLM's unverified output to write directly to the live question bank. In particular, the following must remain faculty-controlled:
- Repairs whose taxonomy entry has \`auto: false\`: identical options, diagrams, wrong-question matches, unsound questions, chapter changes and syllabus claims.
- Any proposed edit that changes a question's meaning, answer semantics, multiple options, a diagram/image, or a broad HTML/MathML block.
- Any edit with an ambiguous/missing exact match, unsupported field, low or conflicting evidence, or stale question version.

For taxonomy-\`auto: true\` repairs, an automated path should still require independently verified evidence, exact field-scope validation, one exact mutation, a question-version check, an immutable audit record and a rollback path. The assignment's \`auto_apply\` value is a routing candidate; it is not evidence that the current static demo actually changed a production record. The current demo records faculty actions in browser-local storage.

## One metric for week one

**Median time to verified resolution for genuine answer-key defects**, measured from the first student report to a faculty-confirmed correction in the source of truth. Segment it by auto-eligible versus faculty-review cases and report the 90th percentile too. This ties speed to correctness: a fast but wrong patch is not a success.

## One idea beyond the brief: pre-flight question quality checks

Run a "shadow audit" when a question is authored or imported—not only after a student reports it. Use a blind solver for supported question types plus deterministic checks for missing options, malformed MathML, missing referenced images, duplicate options and answer/solution mismatches. Send uncertain cases to faculty before the question is exposed to students.

The supplied fixture contains two candidate latent defects surfaced by the project's bonus scan; they should be confirmed by a subject expert before any production correction. This turns the report loop into prevention while preserving faculty control over academic judgement.
