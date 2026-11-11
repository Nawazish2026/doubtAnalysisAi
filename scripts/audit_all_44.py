import json, re

with open("acadza-report-fix/all_reports_dump.json") as f:
    items = json.load(f)

for idx, item in enumerate(items):
    r = item["report"]
    q = item["question"]
    rid = r["reportId"]
    qid = r["questionId"]
    comm = r["comment"]
    qtype = q.get("questionType", "")
    content = q.get(qtype, {})
    ans = content.get("answer")
    q_raw = content.get("question", "")
    sol_raw = content.get("solution", "")
    print(f"REPORT #{idx+1:02d}: {rid} | QID: {qid} | Type: {qtype} | Stored Ans: {ans}")
    print(f"Comment: {comm}")
    print("--- Question Text ---")
    print(q_raw[:300].strip())
    print("--- Stored Solution ---")
    print(sol_raw[:300].strip())
    print("\n" + "#"*70 + "\n")
