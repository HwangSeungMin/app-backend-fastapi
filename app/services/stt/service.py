import azure.cognitiveservices.speech as speechsdk
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv(override=True)


class AzureSpeechService:
    """Azure Speech Service를 사용한 STT 서비스"""

    def __init__(self):
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.speech_region = os.getenv("AZURE_SPEECH_REGION")

    def transcribe_audio(self, audio_data: bytes) -> dict:
        """
        WAV 오디오 데이터를 텍스트로 변환 (STT)
        - 형식: WAV (PCM)
        - 샘플레이트: 16000 Hz
        - 채널: Mono
        - 비트: 16bit
        """
        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region
        )
        speech_config.speech_recognition_language = "ko-KR"

        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(audio_data)
        audio_stream.close()

        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        result = speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {
                "success": True,
                "text": result.text,
                "message": "음성 인식 성공"
            }
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {
                "success": False,
                "text": "",
                "message": "음성을 인식할 수 없습니다"
            }
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            return {
                "success": False,
                "text": "",
                "message": f"오류: {cancellation.reason} - {cancellation.error_details}"
            }
        else:
            return {
                "success": False,
                "text": "",
                "message": f"오류: {result.reason}"
            }


class LLMService:
    """Azure OpenAI를 사용한 LLM 서비스 (STT 후처리용)"""

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        self.extraction_prompt = """당신은 의약품 복용 정보 추출 전문가입니다.
사용자가 제공하는 텍스트(음성 인식 결과)에서 의약품 복용 정보를 추출하여 정확한 JSON 형식으로 반환하세요.

## 추출해야 할 정보:
1. medication_name: 약 이름 (언급되지 않으면 null)
2. total_duration_days: 총 복용 일수 (예: "4일분" → 4)
3. daily_frequency: 하루 복용 횟수 (예: "1일 3회" → 3)
4. meal_context: 식사와의 관계
   - "pre_meal": 식전
   - "post_meal": 식후
   - "at_bedtime": 취침 전
   - null: 언급 없음
5. specific_offset_minutes: 식사 기준 시간 (분 단위)
   - "식후 30분" → 30
   - "식전 1시간" → 60
   - 언급 없으면 null
6. special_instructions: 기타 특별 지시사항 (없으면 null)

## 음성 인식 오류 보정:
- "113회" → "1일 3회"로 해석
- "이일" → "2일"로 해석
- 숫자와 단위가 붙어있는 경우 적절히 분리

## 응답 형식:
반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 반환하세요.

{
  "medication_name": "String 또는 null",
  "total_duration_days": "Integer 또는 null",
  "daily_frequency": "Integer 또는 null",
  "meal_context": "pre_meal|post_meal|at_bedtime 또는 null",
  "specific_offset_minutes": "Integer 또는 null",
  "special_instructions": "String 또는 null"
}"""

    def extract_medication_info(self, stt_text: str) -> dict:
        """STT 텍스트에서 의약품 복용 정보를 추출"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": self.extraction_prompt
                    },
                    {
                        "role": "user",
                        "content": f"다음 음성 인식 결과에서 의약품 복용 정보를 추출해주세요:\n\n{stt_text}"
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )

            response_text = response.choices[0].message.content

            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extracted_data = json.loads(json_str)

                return {
                    "success": True,
                    "data": extracted_data,
                    "raw_response": response_text,
                    "message": "데이터 추출 성공"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "raw_response": response_text,
                    "message": "JSON 파싱 실패"
                }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "data": None,
                "raw_response": response_text if 'response_text' in locals() else None,
                "message": f"JSON 파싱 오류: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "raw_response": None,
                "message": f"API 오류: {str(e)}"
            }


class STTService:
    """STT + LLM 통합 서비스"""

    def __init__(self):
        self.speech_service = AzureSpeechService()
        self.llm_service = LLMService()

    def transcribe_only(self, audio_data: bytes) -> dict:
        """음성을 텍스트로만 변환 (STT only)"""
        return self.speech_service.transcribe_audio(audio_data)

    def extract_from_audio(self, audio_data: bytes) -> dict:
        """음성에서 의약품 정보 추출 (STT + LLM)"""
        stt_result = self.speech_service.transcribe_audio(audio_data)

        if not stt_result["success"]:
            return {
                "success": False,
                "stt_text": "",
                "data": None,
                "message": stt_result["message"]
            }

        stt_text = stt_result["text"]
        llm_result = self.llm_service.extract_medication_info(stt_text)

        return {
            "success": llm_result["success"],
            "stt_text": stt_text,
            "data": llm_result["data"],
            "message": llm_result["message"]
        }

    def extract_from_text(self, text: str) -> dict:
        """텍스트에서 의약품 정보 추출 (LLM only)"""
        llm_result = self.llm_service.extract_medication_info(text)

        return {
            "success": llm_result["success"],
            "input_text": text,
            "data": llm_result["data"],
            "message": llm_result["message"]
        }
