import asyncpg
from fastapi import APIRouter, Depends, Query

from app.db import get_db
from app.dependencies import faculty_user

router = APIRouter(prefix="/api/audit-logs", tags=["Audit"])


@router.get("")
async def list_audit_logs(
    user: dict = Depends(faculty_user),
    db: asyncpg.Connection = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=250),
):
    rows = await db.fetch(
        """select id,actor_id,entity_type,entity_id,action,
                  before_state,after_state,metadata,created_at
           from public.audit_logs order by created_at desc limit $1""",
        limit,
    )
    return [dict(row) for row in rows]
