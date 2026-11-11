from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status

from app.config import settings


@lru_cache
def _jwks_client() -> PyJWKClient:
    url = settings.supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)


def verify_supabase_token(token: str) -> dict[str, Any]:
    issuer = settings.supabase_url.rstrip("/") + "/auth/v1"
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg")

        # Older Supabase projects may still use HS256. Keep this secret server-side only.
        if algorithm == "HS256":
            if not settings.supabase_jwt_secret:
                raise ValueError("HS256 requires SUPABASE_JWT_SECRET on the backend")
            key = settings.supabase_jwt_secret
            algorithms = ["HS256"]
        else:
            signing_key = _jwks_client().get_signing_key_from_jwt(token)
            key = signing_key.key
            algorithms = ["ES256", "RS256", "EdDSA"]

        return jwt.decode(
            token,
            key,
            algorithms=algorithms,
            audience="authenticated",
            issuer=issuer,
            options={"require": ["exp", "sub", "iss", "aud"]},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
