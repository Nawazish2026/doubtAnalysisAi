import pytest
from fastapi import HTTPException

from app.services.proposals import apply_surgical_edit, validate_proposal


def test_exact_single_replacement():
    qtype, content, before, after = apply_surgical_edit(
        "scq", {"question": "Find x. Find y.", "answer": "A"},
        {"field": "answer", "find": "A", "replace": "B"},
    )
    assert qtype == "scq"
    assert content["answer"] == "B"
    assert before == "A" and after == "B"


def test_ambiguous_replacement_is_rejected():
    with pytest.raises(HTTPException) as error:
        apply_surgical_edit(
            "scq", {"question": "A appears twice: A", "answer": "A"},
            {"field": "question", "find": "A", "replace": "B"},
        )
    assert error.value.status_code == 409


def test_repair_scope_is_enforced():
    with pytest.raises(HTTPException) as error:
        validate_proposal("spelling", {"field": "answer", "find": "A", "replace": "B"})
    assert error.value.status_code == 422
