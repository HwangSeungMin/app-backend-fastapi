from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_rag():
    return {"message": "RAG endpoint"}
