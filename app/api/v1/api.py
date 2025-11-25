from fastapi import APIRouter
from app.api.v1.endpoints.ocr import routes as ocr
from app.api.v1.endpoints.stt import routes as stt
from app.api.v1.endpoints.chatbot import routes as chatbot
from app.api.v1.endpoints.rag import routes as rag
from app.api.v1.endpoints.alarms import routes as alarms
from app.api.v1.endpoints.users import routes as users

api_router = APIRouter()
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(stt.router, prefix="/stt", tags=["stt"])
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(alarms.router, prefix="/alarms", tags=["alarms"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
