from copy import deepcopy

from fastapi import HTTPException

from app.taxonomy import load_taxonomy


def validate_proposal(repair: str, edit: dict | None) -> dict:
    taxonomy = load_taxonomy()
    repair_config = taxonomy.get("repairs", {}).get(repair)
    if not repair_config:
        raise HTTPException(status_code=422, detail="Unknown repair type")

    if not edit:
        if repair_config.get("fields"):
            raise HTTPException(status_code=422, detail="This repair requires a proposed edit")
        return repair_config

    field = edit.get("field")
    if field not in repair_config.get("fields", []):
        raise HTTPException(status_code=422, detail=f"Repair '{repair}' cannot edit field '{field}'")
    if not isinstance(edit.get("find"), str) or not isinstance(edit.get("replace"), str):
        raise HTTPException(status_code=422, detail="Edit find/replace must be strings")
    if not edit["find"]:
        raise HTTPException(status_code=422, detail="Edit search text cannot be empty")
    return repair_config


def apply_surgical_edit(question_type: str, content: dict, edit: dict) -> tuple[str, dict, object, object]:
    """Apply exactly one textual replacement; no broad/ambiguous replacements."""
    field = edit["field"]
    find = edit["find"]
    replacement = edit["replace"]

    if field == "questionType":
        current = question_type
        if current.count(find) != 1:
            raise HTTPException(status_code=409, detail="Question type text is no longer an exact match")
        return replacement, content, current, replacement

    updated = deepcopy(content)
    current = updated.get(field)
    if not isinstance(current, str):
        raise HTTPException(
            status_code=422,
            detail=f"Field '{field}' is not a text field; this edit format cannot safely change it",
        )
    if current.count(find) != 1:
        raise HTTPException(
            status_code=409,
            detail="Proposed text must match exactly once; reload and create a fresh proposal",
        )
    new_value = current.replace(find, replacement, 1)
    updated[field] = new_value
    return question_type, updated, current, new_value
