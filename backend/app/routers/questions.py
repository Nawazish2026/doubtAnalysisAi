import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_db
from app.dependencies import current_user, faculty_user

router = APIRouter(prefix="/api/questions", tags=["Questions"])


@router.get("")
async def list_questions(
    user: dict = Depends(current_user),
    db: asyncpg.Connection = Depends(get_db),
    search: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=100),
):
    rows = await db.fetch(
        """select id,question_type,subject,chapter,level,version,updated_at
           from public.questions
           where is_active=true
             and ($1::text is null or id ilike '%' || $1 || '%'
                  or coalesce(subject,'') ilike '%' || $1 || '%'
                  or coalesce(chapter,'') ilike '%' || $1 || '%')
           order by updated_at desc limit $2""",
        search, limit,
    )
    return [dict(row) for row in rows]


@router.get("/{question_id}")
async def get_question(
    question_id: str,
    user: dict = Depends(current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    row = await db.fetchrow(
        """select id,question_type,subject,chapter,level,content,version,updated_at
           from public.questions where id=$1 and is_active=true""",
        question_id,
    )
    if not row:
        raise HTTPException(404, "Question not found")
    return dict(row)


@router.get("/{question_id}/history")
async def question_history(
    question_id: str,
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        """select version,snapshot,changed_by,change_reason,created_at
           from public.question_versions where question_id=$1
           order by version desc""",
        question_id,
    )
    return [dict(row) for row in rows]
