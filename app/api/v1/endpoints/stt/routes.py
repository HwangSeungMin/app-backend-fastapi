from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.stt.service import STTService

router = APIRouter()

stt_service = STTService()


class TextInput(BaseModel):
    text: str


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    음성 파일을 텍스트로 변환 (STT only)

    - audio: WAV 형식의 오디오 파일 (16kHz, mono, 16bit)
    - returns: 변환된 텍스트
    """
    if not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="WAV 파일만 지원합니다 (16kHz, mono, 16bit)")

    audio_data = await audio.read()
    result = stt_service.transcribe_only(audio_data)

    return result


@router.post("/extract")
async def extract_from_voice(audio: UploadFile = File(...)):
    """
    음성 파일에서 의약품 복용 정보 추출 (STT + LLM)

    - audio: WAV 형식의 오디오 파일 (16kHz, mono, 16bit)
    - returns: 구조화된 의약품 복용 정보 JSON
    """
    if not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="WAV 파일만 지원합니다 (16kHz, mono, 16bit)")

    audio_data = await audio.read()
    result = stt_service.extract_from_audio(audio_data)

    if not result["success"] and result["data"] is None and result["stt_text"] == "":
        raise HTTPException(status_code=500, detail=result["message"])

    return result


@router.post("/extract-text")
async def extract_from_text(input: TextInput):
    """
    텍스트에서 의약품 복용 정보 추출 (LLM only, 테스트용)

    - text: 음성 인식 결과 또는 직접 입력 텍스트
    - returns: 구조화된 의약품 복용 정보 JSON
    """
    result = stt_service.extract_from_text(input.text)

    return result


@router.get("/health")
async def health_check():
    """STT 서비스 상태 확인"""
    return {"status": "ok", "service": "Azure Speech STT + LLM"}
