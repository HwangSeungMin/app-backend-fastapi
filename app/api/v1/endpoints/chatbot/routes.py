from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_chatbot():
    return {"message": "Chatbot endpoint"}
