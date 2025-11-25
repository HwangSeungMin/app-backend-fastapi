from pydantic import BaseModel

class STTRequest(BaseModel):
    audio_url: str

class STTResponse(BaseModel):
    transcript: str
