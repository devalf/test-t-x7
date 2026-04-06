from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_campaigns():
    # Implemented in Phase 7
    return []


@router.post("/create-all")
async def create_all_campaigns():
    # Implemented in Phase 7
    return []
