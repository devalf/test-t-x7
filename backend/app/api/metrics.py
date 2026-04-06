from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_metrics():
    # Implemented in Phase 7
    return []


@router.get("/suggestions")
async def list_suggestions():
    # Implemented in Phase 8
    return []


@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(suggestion_id: str):
    # Implemented in Phase 8
    return {"detail": "not implemented"}
