from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    question_id: str = Field(min_length=1, max_length=128)
    comment: str = Field(min_length=3, max_length=3000)
    source: Literal["web", "android", "ios"] = "web"


class ProposalEdit(BaseModel):
    field: str = Field(min_length=1, max_length=80)
    find: str = Field(min_length=1, max_length=12000)
    replace: str = Field(max_length=12000)


class ProposalCreate(BaseModel):
    repair: str = Field(min_length=1, max_length=80)
    edit: ProposalEdit | None = None
    note: str | None = Field(default=None, max_length=2000)


class ReviewRequest(BaseModel):
    expected_question_version: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=1000)


class RejectRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)


class ReportOut(BaseModel):
    id: UUID
    status: str
    created_at: str | None = None
