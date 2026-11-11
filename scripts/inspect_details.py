import json, re
from pathlib import Path

with open(Path(__file__).with_name("all_reports_dump.json"), encoding="utf-8") as f:
    items = json.load(f)

for i, it in enumerate(items):
    r = it["report"]
    q = it["question"]
    qtype = q.get("questionType", "")
    content = q.get(qtype, {})
    rid = r["reportId"]
    qid = r["questionId"]
    ans = content.get("answer")
    comm = r["comment"]
    
    print(f"=== [{i+1}] {rid} | QID: {qid} | Type: {qtype} | Ans: {ans} ===")
    print(f"Comment: {comm}")
    print("Question raw:")
    print(content.get("question", ""))
    print("Solution raw:")
    print(content.get("solution", ""))
    print("\n" + "="*80 + "\n")
