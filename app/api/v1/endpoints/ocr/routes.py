from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_ocr():
    return {"message": "OCR endpoint"}
