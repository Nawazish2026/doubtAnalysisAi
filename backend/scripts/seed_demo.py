"""Import the repository's anonymized fixture JSON into a fresh database."""
import asyncio
import json
import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import asyncpg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "backend" / ".env")


async def main():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Set DATABASE_URL in backend/.env before seeding")

    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=3)
    try:
        questions = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
        reports = json.loads((ROOT / "data/reports.json").read_text(encoding="utf-8"))
        results = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))

        async with pool.acquire() as db:
            async with db.transaction():
                for q in questions:
                    qtype = q.get("questionType", "")
                    content = q.get(qtype, {})
                    await db.execute(
                        """insert into public.questions
                           (id,question_type,subject,chapter,level,content)
                           values ($1,$2,$3,$4,$5,$6::jsonb)
                           on conflict (id) do nothing""",
                        q["_id"], qtype, q.get("subject"), q.get("chapter"),
                        q.get("level"), json.dumps(content),
                    )

                report_ids = {}
                for report in reports:
                    rid = report["reportId"]
                    db_id = uuid5(NAMESPACE_URL, "ac adza-demo-report:" + rid)
                    report_ids[rid] = db_id
                    await db.execute(
                        """insert into public.reports
                           (id,external_report_id,question_id,student_ref,source,comment,status,created_at)
                           values ($1,$2,$3,$4,$5,$6,'faculty_review',
                                   coalesce($7::timestamptz,now()))
                           on conflict (external_report_id) do nothing""",
                        db_id, rid, report["questionId"], report.get("studentId"),
                        report.get("source", "import"), report["comment"],
                        report.get("reportedAt"),
                    )

                for result in results:
                    rid = result["reportId"]
                    if rid not in report_ids:
                        continue
                    await db.execute(
                        """insert into public.triage_results
                           (report_id,verdict,repair,edit,route,confidence,evidence,student_reply,engine_version)
                           select $1,$2,$3,$4::jsonb,$5,$6,$7,$8,'fixture-results-v1'
                           where not exists (
                             select 1 from public.triage_results where report_id=$1
                           )""",
                        report_ids[rid], result["verdict"], result.get("repair"),
                        json.dumps(result.get("edit")) if result.get("edit") is not None else None,
                        result["route"], result.get("confidence"),
                        result.get("evidence"), result.get("student_reply"),
                    )
        print(f"Imported {len(questions)} questions, {len(reports)} reports, {len(results)} triage results.")
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
