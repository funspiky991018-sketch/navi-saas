from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/status")
def auth_status():
    return {
        "auth": "ready"
    }