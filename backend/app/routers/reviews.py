from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends

from app.db import get_db
from app.dependencies import faculty_user
from app.schemas import ReviewRequest, RejectRequest
from app.services.approval import approve_proposal, reject_proposal

router = APIRouter(prefix="/api/reports", tags=["Faculty Reviews"])


@router.post("/{report_id}/proposals/{proposal_id}/approve")
async def approve(
    report_id: UUID,
    proposal_id: UUID,
    body: ReviewRequest,
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
):
    return await approve_proposal(
        db,
        report_id=report_id,
        proposal_id=proposal_id,
        faculty_id=UUID(user["id"]),
        expected_question_version=body.expected_question_version,
        reason=body.reason,
    )


@router.post("/{report_id}/proposals/{proposal_id}/reject")
async def reject(
    report_id: UUID,
    proposal_id: UUID,
    body: RejectRequest,
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
):
    return await reject_proposal(
        db,
        report_id=report_id,
        proposal_id=proposal_id,
        faculty_id=UUID(user["id"]),
        reason=body.reason,
    )
