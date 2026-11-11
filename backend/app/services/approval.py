from fastapi import HTTPException

from app.services.proposals import apply_surgical_edit, validate_proposal


async def approve_proposal(
    db,
    *,
    report_id,
    proposal_id,
    faculty_id,
    expected_question_version: int,
    reason: str,
):
    async with db.transaction():
        report = await db.fetchrow(
            "select * from public.reports where id=$1 for update", report_id
        )
        if not report:
            raise HTTPException(404, "Report not found")
        if report["status"] not in ("faculty_review", "pending_triage"):
            raise HTTPException(409, "Report is no longer awaiting review")

        proposal = await db.fetchrow(
            """select * from public.repair_proposals
               where id=$1 and report_id=$2 for update""",
            proposal_id, report_id,
        )
        if not proposal or proposal["status"] != "pending":
            raise HTTPException(409, "Proposal is missing or already reviewed")

        question = await db.fetchrow(
            "select * from public.questions where id=$1 for update",
            report["question_id"],
        )
        if not question:
            raise HTTPException(404, "Question not found")
        if question["version"] != expected_question_version:
            raise HTTPException(409, "Question changed; refresh before approving")
        if proposal["base_question_version"] != question["version"]:
            raise HTTPException(409, "Proposal is based on an older question version")

        edit = proposal["edit"]
        taxonomy = validate_proposal(proposal["repair"], edit)

        # Taxonomy entries with no editable fields are decision-only. Faculty can
        # confirm the review outcome, but this endpoint will not mutate question data.
        if not edit:
            await db.execute(
                """update public.repair_proposals
                   set status='approved', reviewed_by=$2, reviewed_at=now()
                   where id=$1""",
                proposal_id, faculty_id,
            )
            await db.execute(
                """update public.reports set status='approved', updated_at=now()
                   where id=$1""",
                report_id,
            )
            await db.execute(
                """insert into public.review_decisions
                   (report_id,proposal_id,faculty_id,action,reason)
                   values ($1,$2,$3,'approved',$4)""",
                report_id, proposal_id, faculty_id, reason,
            )
            await db.execute(
                """insert into public.audit_logs
                   (actor_id,entity_type,entity_id,action,before_state,after_state,metadata)
                   values ($1,'report',$2,'faculty_review_approved',$3,$4,$5)""",
                faculty_id, str(report_id),
                {"status": report["status"]},
                {"status": "approved"},
                {"proposal_id": str(proposal_id), "question_changed": False,
                 "manual_followup_required": True, "repair": proposal["repair"]},
            )
            return {
                "report_id": str(report_id),
                "question_id": question["id"],
                "status": "approved",
                "question_changed": False,
                "question_version": question["version"],
                "manual_followup_required": True,
                "taxonomy_auto_allowed": bool(taxonomy.get("auto")),
            }

        old_snapshot = {
            "question_type": question["question_type"],
            "subject": question["subject"],
            "chapter": question["chapter"],
            "level": question["level"],
            "content": question["content"],
            "version": question["version"],
        }
        new_type, new_content, before_value, after_value = apply_surgical_edit(
            question["question_type"], question["content"], edit
        )
        new_version = question["version"] + 1

        await db.execute(
            """insert into public.question_versions
               (question_id,version,snapshot,changed_by,change_reason)
               values ($1,$2,$3,$4,$5)""",
            question["id"], question["version"], old_snapshot, faculty_id, reason,
        )
        await db.execute(
            """update public.questions
               set question_type=$2,content=$3,version=$4,updated_at=now()
               where id=$1""",
            question["id"], new_type, new_content, new_version,
        )
        await db.execute(
            """update public.repair_proposals
               set status='approved',reviewed_by=$2,reviewed_at=now()
               where id=$1""",
            proposal_id, faculty_id,
        )
        await db.execute(
            """update public.reports set status='corrected',updated_at=now()
               where id=$1""",
            report_id,
        )
        await db.execute(
            """insert into public.review_decisions
               (report_id,proposal_id,faculty_id,action,reason)
               values ($1,$2,$3,'approved',$4)""",
            report_id, proposal_id, faculty_id, reason,
        )
        await db.execute(
            """insert into public.audit_logs
               (actor_id,entity_type,entity_id,action,before_state,after_state,metadata)
               values ($1,'question',$2,'approved_correction',$3,$4,$5)""",
            faculty_id, question["id"],
            {"version": question["version"], "value": before_value},
            {"version": new_version, "value": after_value},
            {"report_id": str(report_id), "proposal_id": str(proposal_id),
             "repair": proposal["repair"]},
        )

    return {
        "report_id": str(report_id),
        "question_id": question["id"],
        "status": "corrected",
        "question_changed": True,
        "old_version": question["version"],
        "new_version": new_version,
        "changed_field": edit["field"],
        "taxonomy_auto_allowed": bool(taxonomy.get("auto")),
    }


async def reject_proposal(db, *, report_id, proposal_id, faculty_id, reason: str):
    async with db.transaction():
        report = await db.fetchrow(
            "select * from public.reports where id=$1 for update", report_id
        )
        if not report:
            raise HTTPException(404, "Report not found")
        if report["status"] not in ("faculty_review", "pending_triage"):
            raise HTTPException(409, "Report is no longer awaiting review")
        proposal = await db.fetchrow(
            "select * from public.repair_proposals where id=$1 and report_id=$2 for update",
            proposal_id, report_id,
        )
        if not proposal or proposal["status"] != "pending":
            raise HTTPException(409, "Proposal is missing or already reviewed")

        await db.execute(
            """update public.repair_proposals set status='rejected',
               reviewed_by=$2, reviewed_at=now() where id=$1""",
            proposal_id, faculty_id,
        )
        await db.execute(
            """update public.reports set status='rejected', updated_at=now() where id=$1""",
            report_id,
        )
        await db.execute(
            """insert into public.review_decisions
               (report_id,proposal_id,faculty_id,action,reason)
               values ($1,$2,$3,'rejected',$4)""",
            report_id, proposal_id, faculty_id, reason,
        )
        await db.execute(
            """insert into public.audit_logs
               (actor_id,entity_type,entity_id,action,before_state,after_state,metadata)
               values ($1,'report',$2,'proposal_rejected',$3,$4,$5)""",
            faculty_id, str(report_id),
            {"status": report["status"], "proposal_id": str(proposal_id)},
            {"status": "rejected"},
            {"reason": reason},
        )
    return {"report_id": str(report_id), "status": "rejected"}
