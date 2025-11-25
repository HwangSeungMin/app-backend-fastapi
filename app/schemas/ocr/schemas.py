from pydantic import BaseModel

class OCRRequest(BaseModel):
    image_url: str

class OCRResponse(BaseModel):
    text: str
