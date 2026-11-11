# Acadza Product Manifesto: The Economics of Question Integrity

> **Target Read Time:** 3 minutes (1 page)  
> **Audience:** Leadership & Engineering Teams at Acadza  

---

### 1. Who Loses the Most When a Question is Broken?

The obvious answer is "the student." But that understates the psychological reality. **The student who loses the most is the high-effort, borderline-qualifying aspirant**—the 17-year-old studying 14 hours a day in Kota or Hyderabad whose percentile sits between 97.5 and 99.0.

In JEE Advanced, the cutoff between an IIT seat and rejection is often separated by 2 marks. When this student solves a question correctly, sees the platform mark them wrong, and reads a broken solution:
1. **They don't just lose marks; they lose epistemic confidence.** They spend 45 minutes doubting a fundamental law of physics they knew by heart.
2. **They conclude the platform is untrustworthy.** In competitive exam prep, trust is binary: once an aspirant suspects the answer key is sloppy, they stop practicing full mock exams on the app.

**How our design reflects this:**
- **Zero-Latency Answer Key Corrections:** High-confidence answer key discrepancies (`answer_key` with dual-derivation proof) can auto-apply or jump straight to the top of the faculty queue (Urgency Score 145), stopping the bleed before the next mock test.
- **Pedagogical Empathy in Feedback:** When a student reports an error but was actually wrong (e.g. Report R043 with surface charge density), our response does not dismiss them. It explains the exact conceptual nuance in 2 encouraging sentences. We turn an erroneous report into an active learning moment.

---

### 2. What We Would NEVER Let the AI Auto-Apply (And Why)

We maintain a non-negotiable **Air Gap** between AI suggestions and production mutations for five specific defect categories:

1. **`identical_options` & Missing Distractors:** Creating new options is authored pedagogical content. An AI generating plausible distractors without syllabus calibration can accidentally introduce a second correct answer or an out-of-scope distractor.
2. **`diagram` & Visual Physics/Biology Assets:** An AI cannot autonomously author and inject an unverified circuit schematic, ray optics figure, or histological cross-section into a live exam. A corrupted diagram ruins 100% of future test attempts.
3. **`unsound` Questions (No Correct Option / Two Correct Options):** Determining whether to drop a question, award bonus marks, or rewrite the core stem is an institutional academic policy decision, never an algorithmic one.
4. **`syllabus` Deletions:** Competitive exam syllabi (NTA NEET / JEE) undergo regulatory shifts. Dropping a question from the question bank because a student claimed it was "out of syllabus" risks stripping valid core curriculum without faculty authorization.
5. **Broad Text Rewrites:** We never allow an LLM to rewrite a full question. Edits are bounded strictly to atomic `{field, find, replace}` substrings.

---

### 3. The One Metric We Would Watch in Week 1

> **Metric:** **Time-to-Resolution for Genuine Answer Key Defects ($TTR_{\text{key}}$)**

While generic support systems monitor ticket volume or CSAT, $TTR_{\text{key}}$ measures systemic platform health:
$$\text{TTR}_{\text{key}} = t_{\text{database\_patch\_applied}} - t_{\text{first\_student\_report}}$$

- **Why this metric?** If an answer key is wrong, every minute it stays live pollutes the percentile rankings, leaderboard stats, and confidence of dozens of students taking that test. 
- **Target:** Reduce $TTR_{\text{key}}$ from **72 hours (human-only manual batching) to under 8 minutes** for auto-applied verified defects, and **under 3 hours** for faculty-reviewed cases.

---

### 4. One Idea Beyond This Brief: "The Proactive Shadow Solver"

Currently, the system waits for a student to report an error. **By definition, a student had to suffer before we took action.**

**Our Pitch: Autonomous Pre-Flight Ingestion Auditing**  
Instead of reactive reporting, run an asynchronous **Shadow Solver Agent** across the entire 8-lakh question bank:
1. Every time a question is authored or imported via DTS, the agent solves it blind, matches the output against the answer key, and tests for leaky MathML (`<mspace>`), missing figures (`quesImages: []` when text says "as shown in figure"), and OCR typos.
2. In our audit of Acadza's 43 sample questions, **this proactive approach immediately caught 2 latent defects on questions zero students had reported** (`68dea87d` with broken markup and `68dea657` with OCR variable corruption).
3. By fixing questions *before* they ever enter a student's mock test, Acadza eliminates question defects at the source.

