from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.db import get_db
from app.dependencies import current_user, faculty_user
from app.schemas import ReportCreate, ProposalCreate
from app.services.proposals import validate_proposal

router = APIRouter(prefix="/api", tags=["Reports"])


@router.post("/reports", status_code=201)
async def create_report(
    body: ReportCreate,
    user: dict = Depends(current_user),
    db: asyncpg.Connection = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    question = await db.fetchrow(
        "select id from public.questions where id=$1 and is_active=true",
        body.question_id,
    )
    if not question:
        raise HTTPException(404, "Question not found")

    report = await db.fetchrow(
        """insert into public.reports
           (question_id, student_user_id, source, comment, status, idempotency_key)
           values ($1,$2,$3,$4,'faculty_review',$5)
           on conflict (student_user_id,idempotency_key)
             where student_user_id is not null and idempotency_key is not null
           do nothing
           returning id,status,created_at""",
        body.question_id, UUID(user["id"]), body.source, body.comment, idempotency_key,
    )
    if not report and idempotency_key:
        prior = await db.fetchrow(
            """select id,status,created_at from public.reports
               where student_user_id=$1 and idempotency_key=$2""",
            UUID(user["id"]), idempotency_key,
        )
        if prior:
            return {"id": str(prior["id"]), "status": prior["status"], "duplicate": True}
    if not report:
        raise HTTPException(409, "Could not create report; retry with a new idempotency key")

    await db.execute(
        """insert into public.audit_logs
           (actor_id, entity_type, entity_id, action, after_state, metadata)
           values ($1,'report',$2,'student_report_submitted',$3,$4)""",
        UUID(user["id"]), str(report["id"]),
        {"status": "faculty_review", "question_id": body.question_id},
        {"source": body.source},
    )
    # The current triage engine has assignment-specific report-ID rules. New live
    # reports are routed to faculty until a generalized classifier is validated.
    return {"id": str(report["id"]), "status": report["status"], "triage": "manual_review"}


@router.get("/reports")
async def list_my_reports(
    user: dict = Depends(current_user),
    db: asyncpg.Connection = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
):
    rows = await db.fetch(
        """select id,question_id,comment,source,status,created_at,updated_at
           from public.reports where student_user_id=$1
           order by created_at desc limit $2""",
        UUID(user["id"]), limit,
    )
    return [dict(row) for row in rows]


@router.get("/reports/{report_id}")
async def get_my_report(
    report_id: UUID,
    user: dict = Depends(current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    if user["role"] in ("faculty", "admin"):
        row = await db.fetchrow(
            """select r.id,r.question_id,r.comment,r.source,r.status,r.created_at,r.updated_at,
                      t.verdict,t.repair,t.route,t.confidence,t.evidence,t.student_reply,t.edit
               from public.reports r
               left join lateral (
                 select * from public.triage_results tr
                 where tr.report_id=r.id order by tr.created_at desc limit 1
               ) t on true
               where r.id=$1""",
            report_id,
        )
    else:
        row = await db.fetchrow(
            """select r.id,r.question_id,r.comment,r.source,r.status,r.created_at,r.updated_at,
                      t.verdict,t.repair,t.route,t.confidence,t.student_reply
               from public.reports r
               left join lateral (
                 select * from public.triage_results tr
                 where tr.report_id=r.id order by tr.created_at desc limit 1
               ) t on true
               where r.id=$1 and r.student_user_id=$2""",
            report_id, UUID(user["id"]),
        )
    if not row:
        raise HTTPException(404, "Report not found")
    return dict(row)


@router.get("/faculty/queue")
async def faculty_queue(
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
    status: str = Query(default="open", pattern="^(open|all|corrected|rejected)$"),
    limit: int = Query(default=100, ge=1, le=250),
):
    status_filter = "" if status == "all" else (
        "and r.status in ('faculty_review','pending_triage')" if status == "open"
        else "and r.status=$1"
    )
    select_sql = """
        select r.id,r.question_id,r.comment,r.source,r.status,r.created_at,
               q.question_type,q.subject,q.chapter,q.level,q.content,q.version,
               t.verdict,t.repair as triage_repair,t.route,t.confidence,t.evidence,
               t.student_reply,t.edit as triage_edit,
               coalesce(p.repair,t.repair) as repair,
               coalesce(p.edit,t.edit) as edit,
               p.id as proposal_id,p.status as proposal_status,
               p.base_question_version
        from public.reports r
        join public.questions q on q.id=r.question_id
        left join lateral (
          select * from public.triage_results t0
          where t0.report_id=r.id order by t0.created_at desc limit 1
        ) t on true
        left join lateral (
          select * from public.repair_proposals p0
          where p0.report_id=r.id order by p0.created_at desc limit 1
        ) p on true
        where true
    """
    if status in ("corrected", "rejected"):
        rows = await db.fetch(
            select_sql + status_filter + " order by r.created_at desc limit $2",
            status, limit,
        )
    else:
        rows = await db.fetch(
            select_sql + status_filter + " order by r.created_at desc limit $1",
            limit,
        )
    return [dict(row) for row in rows]


@router.post("/reports/{report_id}/proposals", status_code=201)
async def create_proposal(
    report_id: UUID,
    body: ProposalCreate,
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
):
    taxonomy = validate_proposal(body.repair, body.edit.model_dump() if body.edit else None)
    edit = body.edit.model_dump() if body.edit else None

    async with db.transaction():
        report = await db.fetchrow(
            """select r.id,r.question_id,r.status,q.version
               from public.reports r join public.questions q on q.id=r.question_id
               where r.id=$1 for update of r""",
            report_id,
        )
        if not report:
            raise HTTPException(404, "Report not found")
        if report["status"] not in ("faculty_review", "pending_triage"):
            raise HTTPException(409, "Report is no longer awaiting review")

        await db.execute(
            """update public.repair_proposals set status='superseded'
               where report_id=$1 and status='pending'""",
            report_id,
        )
        proposal = await db.fetchrow(
            """insert into public.repair_proposals
               (report_id,question_id,repair,edit,note,base_question_version,proposed_by)
               values ($1,$2,$3,$4,$5,$6,$7)
               returning id,status,base_question_version""",
            report_id, report["question_id"], body.repair, edit, body.note,
            report["version"], UUID(user["id"]),
        )
        await db.execute(
            """insert into public.audit_logs
               (actor_id,entity_type,entity_id,action,after_state,metadata)
               values ($1,'report',$2,'proposal_created',$3,$4)""",
            UUID(user["id"]), str(report_id),
            {"proposal_id": str(proposal["id"]), "repair": body.repair, "edit": edit},
            {"taxonomy_auto": bool(taxonomy.get("auto"))},
        )
    return dict(proposal)
