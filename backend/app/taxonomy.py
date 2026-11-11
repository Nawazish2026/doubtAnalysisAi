import json
from functools import lru_cache

from app.config import settings


@lru_cache
def load_taxonomy() -> dict:
    with settings.taxonomy_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
