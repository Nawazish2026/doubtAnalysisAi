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

    if idempotency_key:
        prior = await db.fetchrow(
            "select id,status,created_at from public.reports where student_user_id=$1 and idempotency_key=$2",
            UUID(user["id"]), idempotency_key,
        )
        if prior:
            return {"id": str(prior["id"]), "status": prior["status"], "duplicate": True}

    report = await db.fetchrow(
        """insert into public.reports
           (question_id, student_user_id, source, comment, status, idempotency_key)
           values ($1,$2,$3,$4,'faculty_review',$5)
           returning id,status,created_at""",
        body.question_id, UUID(user["id"]), body.source, body.comment, idempotency_key,
    )
    await db.execute(
        """insert into public.audit_logs
           (actor_id, entity_type, entity_id, action, after_state, metadata)
           values ($1,'report',$2,'student_report_submitted',$3,$4)""",
        UUID(user["id"]), str(report["id"]),
        {"status": "faculty_review", "question_id": body.question_id},
        {"source": body.source},
    )
    # Intentionally route new live reports to faculty. The current triage engine
    # contains assignment-specific rules and is not a general-purpose classifier.
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
    if status in ("corrected", "rejected"):
        rows = await db.fetch(
            f"""select r.id,r.question_id,r.comment,r.source,r.status,r.created_at,
                       q.question_type,q.subject,q.chapter,q.content,q.version,
                       p.id as proposal_id,p.repair,p.edit,p.status as proposal_status,p.base_question_version
                from public.reports r join public.questions q on q.id=r.question_id
                left join lateral (
                  select * from public.repair_proposals p0
                  where p0.report_id=r.id order by p0.created_at desc limit 1
                ) p on true
                where true {status_filter}
                order by r.created_at desc limit $2""",
            status, limit,
        )
    else:
        rows = await db.fetch(
            f"""select r.id,r.question_id,r.comment,r.source,r.status,r.created_at,
                       q.question_type,q.subject,q.chapter,q.content,q.version,
                       p.id as proposal_id,p.repair,p.edit,p.status as proposal_status,p.base_question_version
                from public.reports r join public.questions q on q.id=r.question_id
                left join lateral (
                  select * from public.repair_proposals p0
                  where p0.report_id=r.id order by p0.created_at desc limit 1
                ) p on true
                where true {status_filter}
                order by r.created_at desc limit $1""",
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
    report = await db.fetchrow(
        """select r.id,r.question_id,r.status,q.version
           from public.reports r join public.questions q on q.id=r.question_id
           where r.id=$1""",
        report_id,
    )
    if not report:
        raise HTTPException(404, "Report not found")
    if report["status"] not in ("faculty_review", "pending_triage"):
        raise HTTPException(409, "Report is no longer awaiting review")
    edit = body.edit.model_dump() if body.edit else None
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
