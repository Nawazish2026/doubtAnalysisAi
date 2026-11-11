import json
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]

def clean_html_colors(html):
    if not html:
        return ""
    html = re.sub(r'color:\s*(#000000|#000|black);?', '', html, flags=re.IGNORECASE)
    html = re.sub(r'style=[\"\']\s*[\"\']', '', html)
    html = re.sub(r'<span\s*>', '<span>', html)
    return html

with open(PROJECT_DIR / "data/questions.json", "r", encoding="utf-8") as f:
    raw_questions = json.load(f)
    questions_by_id = {q["_id"]: q for q in raw_questions}

with open(PROJECT_DIR / "data/reports.json", "r", encoding="utf-8") as f:
    reports = json.load(f)

with open(PROJECT_DIR / "results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

results_by_rid = {r["reportId"]: r for r in results}
report_ids = {r["reportId"] for r in reports}
missing_questions = {r["questionId"] for r in reports if r["questionId"] not in questions_by_id}
missing_results = report_ids - results_by_rid.keys()
unexpected_results = results_by_rid.keys() - report_ids

if missing_questions:
    raise ValueError(f"Reports reference unknown questions: {sorted(missing_questions)}")
if len(results_by_rid) != len(results):
    raise ValueError("results.json contains duplicate report IDs")
if missing_results:
    raise ValueError(f"results.json is missing reports: {sorted(missing_results)}")
if unexpected_results:
    raise ValueError(f"results.json contains unknown reports: {sorted(unexpected_results)}")

reports_by_qid = {}
for r in reports:
    qid = r["questionId"]
    reports_by_qid.setdefault(qid, []).append(r)

console_items = []

for qid, q_reports in reports_by_qid.items():
    q = questions_by_id[qid]
    qtype = q.get("questionType", "")
    content = q.get(qtype, {})
    
    triage_records = [results_by_rid[r["reportId"]] for r in q_reports if r["reportId"] in results_by_rid]
    primary_triage = triage_records[0] if triage_records else {}
    
    urgency = len(q_reports) * 25
    repair = primary_triage.get("repair")
    route = primary_triage.get("route")
    
    if repair == "answer_key":
        urgency += 50
    elif repair in ["diagram", "identical_options", "wrong_chapter", "syllabus"]:
        urgency += 45
    elif repair in ["stem_data", "option_repair"]:
        urgency += 35
    elif repair in ["solution_fix", "type_mismatch"]:
        urgency += 25
    elif repair in ["spelling", "exam_reference", "markup_leak", "answer_form"]:
        urgency += 15

    if route == "faculty_review":
        urgency += 40
    elif route == "auto_apply":
        urgency += 20

    edit = primary_triage.get("edit")
    before_text = ""
    after_text = ""
    target_field = ""
    
    if edit:
        target_field = edit.get("field", "")
        find_str = edit.get("find", "")
        replace_str = edit.get("replace", "")
        source = q if target_field == "questionType" else content
        original_val = source.get(target_field, "")
        if target_field == "answer":
            before_text = str(original_val)
            after_text = str(replace_str)
        else:
            before_text = find_str
            after_text = replace_str

    item = {
        "questionId": qid,
        "questionType": qtype,
        "subject": q.get("subject", "General"),
        "chapter": q.get("chapter", "General"),
        "level": q.get("level", "MEDIUM"),
        "storedAnswer": content.get("answer"),
        "rawQuestionHtml": clean_html_colors(content.get("question", "")),
        "rawSolutionHtml": clean_html_colors(content.get("solution", "")),
        "quesImages": content.get("quesImages", []),
        "solutionImages": content.get("solutionImages", []),
        "reportCount": len(q_reports),
        "urgencyScore": urgency,
        "reports": q_reports,
        "primaryTriage": primary_triage,
        "diff": {
            "field": target_field,
            "find": edit.get("find", "") if edit else "",
            "replace": edit.get("replace", "") if edit else "",
            "before": before_text,
            "after": after_text
        } if edit else None
    }
    console_items.append(item)

console_items.sort(key=lambda x: x["urgencyScore"], reverse=True)

with open(PROJECT_DIR / "console_data.json", "w", encoding="utf-8") as f:
    json.dump(console_items, f, indent=2)

print(f"Generated console_data.json with {len(console_items)} grouped questions")
