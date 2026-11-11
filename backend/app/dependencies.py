from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import asyncpg

from app.db import get_db
from app.security import verify_supabase_token


bearer = HTTPBearer(auto_error=False)


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: asyncpg.Connection = Depends(get_db),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in required")

    claims = verify_supabase_token(credentials.credentials)
    try:
        user_id = UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid user identity") from exc

    profile = await db.fetchrow(
        "SELECT id::text AS id, role FROM public.profiles WHERE id = $1",
        user_id,
    )
    if not profile:
        raise HTTPException(status_code=403, detail="User profile is not provisioned")

    return {
        "id": profile["id"],
        "role": profile["role"],
        "email": claims.get("email"),
    }


async def faculty_user(user: dict = Depends(current_user)) -> dict:
    if user["role"] not in ("faculty", "admin"):
        raise HTTPException(status_code=403, detail="Faculty access required")
    return user
