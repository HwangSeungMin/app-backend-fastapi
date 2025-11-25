from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_stt():
    return {"message": "STT endpoint"}
