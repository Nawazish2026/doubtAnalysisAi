import json, re

with open("acadza-report-fix/all_reports_dump.json") as f:
    items = json.load(f)

def clean(s):
    if not s: return ""
    return " ".join(re.sub(r"<[^>]+>", " ", str(s)).split())

for i, it in enumerate(items):
    r = it["report"]
    q = it["question"]
    qtype = q.get("questionType", "")
    content = q.get(qtype, {})
    rid = r["reportId"]
    qid = r["questionId"]
    ans = content.get("answer")
    comm = r["comment"]
    q_txt = clean(content.get("question"))
    sol_txt = clean(content.get("solution"))
    print(f"[{i+1}/44] {rid} | QID: {qid} | Type: {qtype} | Ans: {ans}")
    print(f"  Comment: {comm}")
    print(f"  Q: {q_txt[:200]}")
    print(f"  Sol: {sol_txt[:200]}")
    print("-" * 60)
