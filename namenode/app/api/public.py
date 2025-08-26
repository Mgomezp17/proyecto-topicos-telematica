from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/test")
def test_endpoint():
    """Endpoint de prueba público"""
    return {"message": "Public test endpoint working"}
