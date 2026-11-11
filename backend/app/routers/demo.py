"""Unauthenticated actions for the isolated, seeded Acadza demo dataset.

These endpoints deliberately cannot read or mutate reports outside the explicit
demo_report_allowlist. They are for a shared public demo, not production review.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Literal

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.db import get_db
from app.services.proposals import apply_surgical_edit, validate_proposal

router = APIRouter(prefix="/api/demo", tags=["Public Demo"])


class DemoEdit(BaseModel):
    field: str = Field(min_length=1, max_length=80)
    find: str = Field(min_length=1, max_length=12000)
    replace: str = Field(max_length=12000)


class DemoDecision(BaseModel):
    question_id: str = Field(min_length=1, max_length=128)
    action: Literal["reject", "save_edit", "approve"]
    repair: str | None = Field(default=None, max_length=80)
    edit: DemoEdit | None = None
    reason: str | None = Field(default=None, max_length=1000)
    student_reply: str | None = Field(default=None, max_length=3000)


async def _rate_limit(request: Request, db: asyncpg.Connection) -> None:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    ip_hash = sha256(ip.encode("utf-8")).hexdigest()
    count = await db.fetchval(
        """
        insert into public.demo_action_rate_limits(ip_hash, window_start, request_count)
        values ($1, date_trunc('minute', now()), 1)
        on conflict (ip_hash) do update set
          request_count = case
            when public.demo_action_rate_limits.window_start < date_trunc('minute', now()) then 1
            else public.demo_action_rate_limits.request_count + 1
          end,
          window_start = date_trunc('minute', now())
        returning request_count
        """,
        ip_hash,
    )
    if count > 30:
        raise HTTPException(status_code=429, detail="Demo action limit reached. Try again in a minute.")


async def _open_demo_reports(db: asyncpg.Connection, question_id: str):
    rows = await db.fetch(
        """
        select r.id, r.external_report_id, r.question_id, r.status
        from public.reports r
        join public.demo_report_allowlist d
          on d.external_report_id = r.external_report_id
        where r.question_id = $1
          and r.status in ('faculty_review', 'pending_triage')
        order by r.created_at, r.external_report_id
        for update of r
        """,
        question_id,
    )
    if not rows:
        raise HTTPException(
            status_code=409,
            detail="This demo case has already been reviewed or is not in the demo dataset.",
        )
    return rows


async def _record_action(
    db: asyncpg.Connection,
    *,
    report,
    action: str,
    reason: str | None,
    details: dict,
    student_reply: str | None = None,
) -> None:
    saved_details = {**details}
    if student_reply is not None:
        saved_details["student_reply"] = student_reply
    if student_reply is not None:
        await db.execute(
            """update public.triage_results
               set student_reply = $2
               where id = (
                   select id from public.triage_results
                   where report_id = $1
                   order by created_at desc limit 1
               )""",
            report["id"],
            student_reply,
        )
    await db.execute(
        """
        insert into public.demo_review_actions
          (report_id, question_id, action, actor_label, reason, details)
        values ($1, $2, $3, 'Public demo visitor', $4, $5)
        """,
        report["id"],
        report["question_id"],
        action,
        reason,
        saved_details,
    )
    await db.execute(
        """
        insert into public.audit_logs
          (actor_id, entity_type, entity_id, action, after_state, metadata)
        values (null, 'report', $1, $2, $3, $4)
        """,
        str(report["id"]),
        "public_demo_" + action,
        {"status_action": action, "question_id": report["question_id"]},
        {"external_report_id": report["external_report_id"], **saved_details},
    )


@router.get("/state")
async def get_demo_state(db: asyncpg.Connection = Depends(get_db)):
    """Return only the seeded demo rows needed to hydrate the public dashboard."""
    questions = await db.fetch(
        """
        select distinct q.id as question_id, q.content, q.version
        from public.questions q
        join public.reports r on r.question_id = q.id
        join public.demo_report_allowlist d on d.external_report_id = r.external_report_id
        order by q.id
        """
    )
    reports = await db.fetch(
        """
        select r.id::text as id, r.external_report_id as report_id,
               r.question_id, r.status, r.created_at, r.updated_at
        from public.reports r
        join public.demo_report_allowlist d on d.external_report_id = r.external_report_id
        order by r.created_at, r.external_report_id
        """
    )
    proposals = await db.fetch(
        """
        select p.id::text as id, r.external_report_id as report_id,
               p.repair, p.edit, p.note, p.status, p.base_question_version,
               p.created_at
        from public.repair_proposals p
        join public.reports r on r.id = p.report_id
        join public.demo_report_allowlist d on d.external_report_id = r.external_report_id
        order by p.created_at
        """
    )
    actions = await db.fetch(
        """
        select a.id::text as id, r.external_report_id as report_id,
               a.question_id, a.action, a.actor_label, a.reason, a.details,
               a.created_at
        from public.demo_review_actions a
        join public.reports r on r.id = a.report_id
        join public.demo_report_allowlist d on d.external_report_id = r.external_report_id
        order by a.created_at desc
        limit 200
        """
    )
    return {
        "questions": [dict(row) for row in questions],
        "reports": [dict(row) for row in reports],
        "proposals": [dict(row) for row in proposals],
        "actions": [dict(row) for row in actions],
    }


@router.post("/decisions")
async def record_demo_decision(
    body: DemoDecision,
    request: Request,
    db: asyncpg.Connection = Depends(get_db),
):
    """Persist demo decisions without login, restricted to allowlisted fixture rows."""
    await _rate_limit(request, db)

    async with db.transaction():
        question = await db.fetchrow(
            """
            select q.*
            from public.questions q
            where q.id = $1
              and exists (
                select 1 from public.reports r
                join public.demo_report_allowlist d
                  on d.external_report_id = r.external_report_id
                where r.question_id = q.id
              )
            for update
            """,
            body.question_id,
        )
        if not question:
            raise HTTPException(status_code=404, detail="Demo question not found.")

        reports = await _open_demo_reports(db, body.question_id)
        report_ids = [row["id"] for row in reports]
        reason = (body.reason or "").strip() or None

        if body.action == "reject":
            await db.execute(
                """
                update public.repair_proposals
                set status = 'rejected', reviewed_at = now()
                where report_id = any($1::uuid[]) and status = 'pending'
                """,
                report_ids,
            )
            await db.execute(
                """
                update public.reports
                set status = 'rejected', updated_at = now()
                where id = any($1::uuid[])
                """,
                report_ids,
            )
            for report in reports:
                await _record_action(
                    db, report=report, action="rejected", reason=reason, details={},
                    student_reply=body.student_reply,
                )
            return {"ok": True, "action": "rejected", "reports_updated": len(reports)}

        pending = await db.fetchrow(
            """
            select p.repair, p.edit, p.base_question_version
            from public.repair_proposals p
            where p.report_id = any($1::uuid[]) and p.status = 'pending'
            order by p.created_at desc
            limit 1
            """,
            report_ids,
        )

        edit = body.edit.model_dump() if body.edit else (pending["edit"] if pending else None)
        repair = body.repair or (pending["repair"] if pending else None)

        if body.action == "save_edit":
            if not edit or not repair:
                raise HTTPException(status_code=422, detail="A valid repair category and edited fix are required.")
            validate_proposal(repair, edit)
            # Validate the exact replacement now, before recording it as pending.
            apply_surgical_edit(question["question_type"], question["content"], edit)

            await db.execute(
                """
                update public.repair_proposals
                set status = 'superseded'
                where report_id = any($1::uuid[]) and status = 'pending'
                """,
                report_ids,
            )
            for report in reports:
                proposal = await db.fetchrow(
                    """
                    insert into public.repair_proposals
                      (report_id, question_id, repair, edit, note, base_question_version, proposed_by)
                    values ($1, $2, $3, $4, $5, $6, null)
                    returning id::text as id
                    """,
                    report["id"],
                    body.question_id,
                    repair,
                    edit,
                    reason,
                    question["version"],
                )
                await _record_action(
                    db,
                    report=report,
                    action="edited",
                    reason=reason,
                    details={"proposal_id": proposal["id"], "repair": repair, "edit": edit},
                    student_reply=body.student_reply,
                )
            return {
                "ok": True,
                "action": "edited",
                "reports_updated": len(reports),
                "question_version": question["version"],
            }

        # Approve: a pending saved proposal is applied even if the browser
        # doesn't resend its contents. No edit means a decision-only approval.
        if edit:
            if not repair:
                raise HTTPException(status_code=422, detail="Repair category is required for an edited approval.")
            validate_proposal(repair, edit)
            if pending and pending["base_question_version"] != question["version"]:
                raise HTTPException(status_code=409, detail="Question changed since the proposal was saved. Refresh and review again.")

            new_type, new_content, before_value, after_value = apply_surgical_edit(
                question["question_type"], question["content"], edit
            )
            old_snapshot = {
                "question_type": question["question_type"],
                "subject": question["subject"],
                "chapter": question["chapter"],
                "level": question["level"],
                "content": question["content"],
                "version": question["version"],
            }
            new_version = question["version"] + 1

            await db.execute(
                """
                insert into public.question_versions
                  (question_id, version, snapshot, changed_by, change_reason)
                values ($1, $2, $3, null, $4)
                """,
                body.question_id,
                question["version"],
                old_snapshot,
                reason or "Public demo correction",
            )
            await db.execute(
                """
                update public.questions
                set question_type = $2, content = $3, version = $4, updated_at = now()
                where id = $1
                """,
                body.question_id,
                new_type,
                new_content,
                new_version,
            )

            # Preserve one proposal per related student report for review history.
            for report in reports:
                existing = await db.fetchrow(
                    """
                    select id from public.repair_proposals
                    where report_id = $1 and status = 'pending'
                    order by created_at desc limit 1
                    """,
                    report["id"],
                )
                if existing:
                    await db.execute(
                        """
                        update public.repair_proposals
                        set status = 'approved', reviewed_at = now(), reviewed_by = null
                        where id = $1
                        """,
                        existing["id"],
                    )
                    proposal_id = str(existing["id"])
                else:
                    proposal_id = await db.fetchval(
                        """
                        insert into public.repair_proposals
                          (report_id, question_id, repair, edit, note, base_question_version, proposed_by, status, reviewed_at)
                        values ($1, $2, $3, $4, $5, $6, null, 'approved', now())
                        returning id::text
                        """,
                        report["id"], body.question_id, repair, edit, reason, question["version"],
                    )
                await db.execute(
                    "update public.reports set status = 'corrected', updated_at = now() where id = $1",
                    report["id"],
                )
                await _record_action(
                    db,
                    report=report,
                    action="approved",
                    reason=reason,
                    details={
                        "proposal_id": proposal_id,
                        "repair": repair,
                        "edit": edit,
                        "question_version": new_version,
                        "before": before_value,
                        "after": after_value,
                    },
                    student_reply=body.student_reply,
                )

            return {
                "ok": True,
                "action": "approved",
                "reports_updated": len(reports),
                "question_id": body.question_id,
                "old_version": question["version"],
                "new_version": new_version,
                "question_changed": True,
            }

        # Decision-only approval: do not alter question content.
        await db.execute(
            """
            update public.repair_proposals
            set status = 'approved', reviewed_at = now(), reviewed_by = null
            where report_id = any($1::uuid[]) and status = 'pending'
            """,
            report_ids,
        )
        await db.execute(
            """
            update public.reports
            set status = 'approved', updated_at = now()
            where id = any($1::uuid[])
            """,
            report_ids,
        )
        for report in reports:
            await _record_action(
                db, report=report, action="approved", reason=reason,
                details={"question_changed": False},
                student_reply=body.student_reply,
            )
        return {"ok": True, "action": "approved", "reports_updated": len(reports), "question_changed": False}
