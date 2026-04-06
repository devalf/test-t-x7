from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_plan():
    # Implemented in Phase 4 (planner agent)
    return {"detail": "not implemented"}
