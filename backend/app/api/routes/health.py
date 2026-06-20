from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
@router.head("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "motionforge-fastapi"}

