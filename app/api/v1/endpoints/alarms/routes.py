from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_alarms():
    return {"message": "Alarms endpoint"}
