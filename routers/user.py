from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/profile")
def profile():
    return {
        "user": "demo"
    }