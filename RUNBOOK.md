# Acadza Report → Fix System Runbook

## Architecture Overview
The system consists of three interconnected layers:
1. **Triage & Repair Engine (`engine/triage_engine.py`)**:
   - Ingestion Layer with Prompt-Injection Neutralizer.
   - Blind STEM Derivation Solver (independent verification).
   - Forensic Comparator matching taxonomy rules.
   - Surgical Mutation & Scope Guardrail Generator.
   - Outputs `results.json` strictly adhering to Acadza ground truth.
2. **Data Aggregator & Urgency Scorer (`engine/prepare_console_data.py`)**:
   - Clusters 44 reports by the 39 questions.
   - Prioritizes by dynamic urgency: $\text{Urgency} = (\text{Reports} \times 25) + \text{Defect Weight} + \text{Block Weight}$.
   - Prepares surgical visual diffs and student response previews.
3. **Faculty Review Console (`index.html` and `console/index.html`)**:
   - Standalone web application with native MathML rendering.
   - High-contrast, dark-mode visual interface optimized for late-night faculty review.
   - Keyboard shortcuts: `J`/`K` (Next/Prev), `A` (Approve), `R` (Reject), `E` (Edit).
   - Audit Trail recording with `localStorage` persistence and JSON export.
   - Proactive Defect Scanner tab uncovering latent defects in unreported questions.

---

## Quickstart Commands

### 1. Run the Triage Engine (Generates `results.json`)
```bash
python3 engine/triage_engine.py
```
*Output: Triages all 44 reports into `results.json` and runs invariant validation.*

### 2. Prepare Console Dataset & Build Console
```bash
python3 engine/prepare_console_data.py
python3 engine/build_console.py
```
*Output: Generates `console_data.json`, `bonus_defects.json`, and updates `index.html`.*

### 3. Launch Local Faculty Console
```bash
# Using Python built-in webserver
python3 -m http.server 3000

# Open in browser
open http://localhost:3000
```

---

## Deployment to Free-Tier Static Hosting (Vercel / Netlify / GitHub Pages)

The Faculty Console is built as a zero-dependency static application (`index.html`).

### Option A: Vercel (1-Click)
```bash
npx vercel --prod
```

### Option B: Netlify
```bash
npx netlify deploy --prod --dir=.
```

### Option C: GitHub Pages
Push the repository to GitHub, go to **Settings → Pages**, select **Deploy from branch (main / root)**, and the site will be live within 60 seconds.

---

## Deliverables Checklist
- [x] **`results.json`**: 44 triaged reports passing 100% of taxonomy schema and invariant checks.
- [x] **Faculty Review Console**: Responsive web app with MathML, diff view, audit log, urgency queue.
- [x] **`PROMPTS.md`**: Complete prompt registry, evolution history, 3 AI failure modes & fixes, design decisions log.
- [x] **`PRODUCT.md`**: 1-page executive manifesto on student impact, safety boundaries, Week 1 metrics, and the Shadow Solver pitch.
- [x] **Bonus Discovery**: 2 latent defects identified in unreported questions (`bonus_defects.json`).

