from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def auth_status():
    """
    Simple auth status check.
    Returns a fixed string for now.
    """
    return {"status": "authenticated", "message": "Auth system is active (MVP placeholder)"}
