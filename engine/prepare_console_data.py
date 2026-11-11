"""
Console Data Pre-processor
Groups questions with their linked reports, triaged results, urgency scores,
and diff previews for the Faculty Review Console.
"""

import json

with open("acadza-report-fix/data/questions.json", "r", encoding="utf-8") as f:
    raw_questions = json.load(f)
    questions_by_id = {q["_id"]: q for q in raw_questions}

with open("acadza-report-fix/data/reports.json", "r", encoding="utf-8") as f:
    reports = json.load(f)

with open("acadza-report-fix/results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

results_by_rid = {r["reportId"]: r for r in results}

# Group reports by questionId
reports_by_qid = {}
for r in reports:
    qid = r["questionId"]
    reports_by_qid.setdefault(qid, []).append(r)

console_items = []

for qid, q_reports in reports_by_qid.items():
    q = questions_by_id.get(qid, {})
    qtype = q.get("questionType", "")
    content = q.get(qtype, {})
    
    # Grab the primary triage record (or aggregate)
    triage_records = [results_by_rid[r["reportId"]] for r in q_reports if r["reportId"] in results_by_rid]
    primary_triage = triage_records[0] if triage_records else {}
    
    # Urgency scoring algorithm:
    # 1. Multi-reports volume weight: each additional report adds 30 points
    # 2. Defect category weight: answer_key = 50, stem_data = 40, identical_options/diagram = 45, spelling = 15
    # 3. Route weight: faculty_review = 40 (blocking), auto_apply = 20, no_change = 0
    urgency = 0
    report_count = len(q_reports)
    urgency += report_count * 25
    
    repair = primary_triage.get("repair")
    route = primary_triage.get("route")
    verdict = primary_triage.get("verdict")
    
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

    # Before / After diff preparation
    edit = primary_triage.get("edit")
    before_text = ""
    after_text = ""
    target_field = ""
    
    if edit:
        target_field = edit.get("field", "")
        find_str = edit.get("find", "")
        replace_str = edit.get("replace", "")
        original_val = content.get(target_field, "")
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
        "rawQuestionHtml": content.get("question", ""),
        "rawSolutionHtml": content.get("solution", ""),
        "quesImages": content.get("quesImages", []),
        "solutionImages": content.get("solutionImages", []),
        "reportCount": report_count,
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

# Sort by urgency descending
console_items.sort(key=lambda x: x["urgencyScore"], reverse=True)

with open("acadza-report-fix/console_data.json", "w", encoding="utf-8") as f:
    json.dump(console_items, f, indent=2)

print(f"Preprocessed {len(console_items)} grouped question cases into acadza-report-fix/console_data.json")
print("Top 5 most urgent cases:")
for it in console_items[:5]:
    print(f"- QID: {it['questionId'][:8]}.. | Urgency: {it['urgencyScore']} | Reports: {it['reportCount']} | Repair: {it['primaryTriage'].get('repair')} | Route: {it['primaryTriage'].get('route')}")
