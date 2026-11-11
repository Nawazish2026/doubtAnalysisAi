import os
import json
from collections.abc import AsyncIterator

import asyncpg
from fastapi import Request


async def _init_connection(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec(
        "json",
        schema="pg_catalog",
        encoder=json.dumps,
        decoder=json.loads,
        format="text",
    )
    await connection.set_type_codec(
        "jsonb",
        schema="pg_catalog",
        encoder=json.dumps,
        decoder=json.loads,
        format="text",
    )


async def create_pool(database_url: str) -> asyncpg.Pool:
    # Vercel runs this API as a serverless function. Keep each warm instance
    # to one DB connection and disable prepared-statement caching so Supabase's
    # transaction pooler (port 6543) can safely serve short-lived invocations.
    on_vercel = os.getenv("VERCEL") == "1"
    pool_size = 1 if on_vercel else 5

    return await asyncpg.create_pool(
        dsn=database_url,
        min_size=0 if on_vercel else 1,
        max_size=pool_size,
        command_timeout=30,
        ssl="require",
        statement_cache_size=0,
        init=_init_connection,
    )


async def get_db(request: Request) -> AsyncIterator[asyncpg.Connection]:
    pool: asyncpg.Pool = request.app.state.pool
    async with pool.acquire() as connection:
        yield connection
