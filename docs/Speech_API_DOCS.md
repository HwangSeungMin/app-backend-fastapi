# 약꼬박 Backend API Documentation

> **약꼬박**: AI 기반 시니어 약 복용 알람 서비스
>
> "사진 한 장, 말 한 마디로 약 알람 설정"

---

## 프로젝트 개요

### 목적
시니어 사용자가 음성으로 약 복용 정보를 말하면, AI가 자동으로 알람 설정에 필요한 정보를 추출하는 백엔드 서비스.

### 기술 스택
- **Framework**: FastAPI (Python 3.13)
- **STT**: Azure Cognitive Services Speech SDK
- **LLM**: Azure OpenAI GPT-4o
- **Server**: Uvicorn

### 데이터 파이프라인
```
┌─────────────────────────────────────────────────────────────────────┐
│  1. Flutter 앱에서 음성 녹음 (WAV: 16kHz, mono, 16bit)              │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  2. POST /api/extract/voice 호출                                    │
│     - 음성 파일 업로드 (multipart/form-data)                        │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  3. Azure Speech STT                                                 │
│     - 음성 → 텍스트 변환                                            │
│     - 예: "113 회, 4일 분 식후 30분 약을 복용해야 돼."              │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  4. Azure OpenAI GPT-4o (LLM 후처리)                                │
│     - STT 오류 보정: "113회" → "1일 3회"                            │
│     - 구조화된 JSON 추출                                            │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  5. JSON 응답 반환                                                   │
│     {                                                                │
│       "daily_frequency": 3,                                         │
│       "total_duration_days": 4,                                     │
│       "meal_context": "post_meal",                                  │
│       "specific_offset_minutes": 30                                 │
│     }                                                                │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│  6. Flutter 앱에서 알람 설정 UI에 값 자동 입력                       │
│     → 사용자 확인/수정 → 알람 생성                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 폴더 구조

```
backend-yakkobak/
├── main.py                 # FastAPI 앱 진입점
├── requirements.txt        # Python 의존성
├── .env                    # 환경변수 (API 키) - git에 포함하지 않음
├── .gitignore
├── routers/
│   ├── __init__.py
│   ├── stt.py              # STT 전용 라우터
│   └── extract.py          # STT + LLM 통합 라우터
├── services/
│   ├── __init__.py
│   ├── azure_speech.py     # Azure STT 서비스
│   └── llm_service.py      # Azure OpenAI LLM 서비스
└── speech_test/
    └── pill-intake-dates.wav  # 테스트용 음성 파일
```

---

## 환경 설정

### requirements.txt
```
fastapi==0.115.0
uvicorn==0.30.6
python-dotenv==1.0.1
azure-cognitiveservices-speech==1.40.0
python-multipart==0.0.9
openai>=1.0.0
```

### .env (환경변수)
```env
# Azure Speech Service
AZURE_SPEECH_KEY="your_speech_key"
AZURE_SPEECH_REGION="westus3"

# Azure OpenAI
AZURE_OPENAI_KEY="your_openai_key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT="gpt-4o"
```

### 서버 실행
```bash
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python main.py
# 또는
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## API 엔드포인트

### Base URL
```
http://localhost:8000
```

### Swagger UI (API 테스트)
```
http://localhost:8000/docs
```

---

## 1. 음성에서 약 정보 추출 (메인 엔드포인트)

### `POST /api/extract/voice`

Flutter 앱에서 주로 사용할 엔드포인트. 음성 파일을 받아 STT + LLM 처리 후 구조화된 JSON 반환.

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `audio`: WAV 파일 (16kHz, mono, 16bit)

#### Flutter/Dart 예시 코드
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<Map<String, dynamic>> extractMedicationInfo(String wavFilePath) async {
  final uri = Uri.parse('http://YOUR_SERVER_IP:8000/api/extract/voice');

  var request = http.MultipartRequest('POST', uri);
  request.files.add(await http.MultipartFile.fromPath('audio', wavFilePath));

  var response = await request.send();
  var responseBody = await response.stream.bytesToString();

  return json.decode(responseBody);
}

// 사용 예시
void main() async {
  final result = await extractMedicationInfo('/path/to/recording.wav');

  if (result['success']) {
    final data = result['data'];
    print('하루 복용 횟수: ${data['daily_frequency']}');
    print('총 복용 일수: ${data['total_duration_days']}');
    print('식사 기준: ${data['meal_context']}');
    print('식사 후 시간(분): ${data['specific_offset_minutes']}');
  }
}
```

#### Response (성공)
```json
{
  "success": true,
  "stt_text": "113 회, 4일 분 식후 30분 약을 복용해야 돼.",
  "data": {
    "medication_name": null,
    "total_duration_days": 4,
    "daily_frequency": 3,
    "meal_context": "post_meal",
    "specific_offset_minutes": 30,
    "special_instructions": null
  },
  "message": "데이터 추출 성공"
}
```

#### Response (실패)
```json
{
  "success": false,
  "stt_text": "",
  "data": null,
  "message": "음성을 인식할 수 없습니다"
}
```

---

## 2. 텍스트에서 약 정보 추출 (테스트/디버깅용)

### `POST /api/extract/text`

STT 없이 텍스트만 LLM에 보내서 JSON 추출. 테스트용.

#### Request
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "text": "1일 3회, 4일분, 식후 30분에 복용하세요"
}
```

#### Flutter/Dart 예시 코드
```dart
Future<Map<String, dynamic>> extractFromText(String text) async {
  final uri = Uri.parse('http://YOUR_SERVER_IP:8000/api/extract/text');

  final response = await http.post(
    uri,
    headers: {'Content-Type': 'application/json'},
    body: json.encode({'text': text}),
  );

  return json.decode(response.body);
}
```

#### Response
```json
{
  "success": true,
  "input_text": "1일 3회, 4일분, 식후 30분에 복용하세요",
  "data": {
    "medication_name": null,
    "total_duration_days": 4,
    "daily_frequency": 3,
    "meal_context": "post_meal",
    "specific_offset_minutes": 30,
    "special_instructions": null
  },
  "message": "데이터 추출 성공"
}
```

---

## 3. STT 전용 (음성 → 텍스트만)

### `POST /api/stt/transcribe`

LLM 없이 STT만 수행. 디버깅용.

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `audio`: WAV 파일 (16kHz, mono, 16bit)

#### Response
```json
{
  "success": true,
  "text": "113 회, 4일 분 식후 30분 약을 복용해야 돼.",
  "message": "음성 인식 성공"
}
```

---

## 4. Health Check

### `GET /api/stt/health`
```json
{"status": "ok", "service": "Azure Speech STT"}
```

### `GET /api/extract/health`
```json
{"status": "ok", "service": "STT + LLM Extract"}
```

---

## JSON 스키마 (data 필드)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `medication_name` | String \| null | 약 이름 | "타이레놀" |
| `total_duration_days` | Integer \| null | 총 복용 일수 | 4 |
| `daily_frequency` | Integer \| null | 하루 복용 횟수 | 3 |
| `meal_context` | String \| null | 식사 기준 | "post_meal" |
| `specific_offset_minutes` | Integer \| null | 식사 기준 시간(분) | 30 |
| `special_instructions` | String \| null | 특별 지시사항 | "물과 함께" |

### meal_context 값
| 값 | 의미 |
|----|------|
| `"pre_meal"` | 식전 |
| `"post_meal"` | 식후 |
| `"at_bedtime"` | 취침 전 |
| `null` | 언급 없음 |

---

## Flutter 통합 가이드

### 1. 음성 녹음 설정
- **포맷**: WAV (PCM)
- **샘플레이트**: 16000 Hz (16kHz)
- **채널**: Mono (1채널)
- **비트**: 16bit

Flutter 패키지 추천: `record` 또는 `flutter_sound`

```dart
// record 패키지 설정 예시
final audioRecorder = AudioRecorder();

await audioRecorder.start(
  const RecordConfig(
    encoder: AudioEncoder.wav,
    sampleRate: 16000,
    numChannels: 1,
    bitRate: 256000,
  ),
  path: filePath,
);
```

### 2. API 호출 흐름
```dart
class MedicationExtractService {
  final String baseUrl;

  MedicationExtractService(this.baseUrl);

  Future<MedicationData?> extractFromVoice(String wavPath) async {
    try {
      final uri = Uri.parse('$baseUrl/api/extract/voice');
      var request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('audio', wavPath));

      var response = await request.send();
      var body = await response.stream.bytesToString();
      var json = jsonDecode(body);

      if (json['success'] == true) {
        return MedicationData.fromJson(json['data']);
      }
      return null;
    } catch (e) {
      print('API 호출 실패: $e');
      return null;
    }
  }
}

class MedicationData {
  final String? medicationName;
  final int? totalDurationDays;
  final int? dailyFrequency;
  final String? mealContext;
  final int? specificOffsetMinutes;
  final String? specialInstructions;

  MedicationData({
    this.medicationName,
    this.totalDurationDays,
    this.dailyFrequency,
    this.mealContext,
    this.specificOffsetMinutes,
    this.specialInstructions,
  });

  factory MedicationData.fromJson(Map<String, dynamic> json) {
    return MedicationData(
      medicationName: json['medication_name'],
      totalDurationDays: json['total_duration_days'],
      dailyFrequency: json['daily_frequency'],
      mealContext: json['meal_context'],
      specificOffsetMinutes: json['specific_offset_minutes'],
      specialInstructions: json['special_instructions'],
    );
  }
}
```

### 3. 알람 시간 계산 로직 (Flutter에서 구현)
```dart
List<DateTime> calculateAlarmTimes(MedicationData data) {
  final alarms = <DateTime>[];
  final now = DateTime.now();

  // 기본 식사 시간 (사용자 설정 또는 디폴트)
  final mealTimes = {
    'breakfast': TimeOfDay(hour: 8, minute: 0),
    'lunch': TimeOfDay(hour: 12, minute: 0),
    'dinner': TimeOfDay(hour: 18, minute: 0),
  };

  // daily_frequency에 따라 알람 시간 분배
  final frequency = data.dailyFrequency ?? 1;
  final offset = data.specificOffsetMinutes ?? 30;
  final isPostMeal = data.mealContext == 'post_meal';

  if (frequency >= 1) {
    alarms.add(_calculateMealAlarm(mealTimes['breakfast']!, offset, isPostMeal));
  }
  if (frequency >= 2) {
    alarms.add(_calculateMealAlarm(mealTimes['lunch']!, offset, isPostMeal));
  }
  if (frequency >= 3) {
    alarms.add(_calculateMealAlarm(mealTimes['dinner']!, offset, isPostMeal));
  }

  return alarms;
}

DateTime _calculateMealAlarm(TimeOfDay meal, int offsetMinutes, bool isAfter) {
  final now = DateTime.now();
  var alarm = DateTime(now.year, now.month, now.day, meal.hour, meal.minute);

  if (isAfter) {
    alarm = alarm.add(Duration(minutes: offsetMinutes));
  } else {
    alarm = alarm.subtract(Duration(minutes: offsetMinutes));
  }

  return alarm;
}
```

---

## 성능 정보

| 단계 | 예상 소요 시간 |
|------|----------------|
| Azure STT | 1-2초 |
| Azure OpenAI GPT-4o | 1-2초 |
| **총 응답 시간** | **2-4초** |

---

## 에러 처리

### HTTP 상태 코드
| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (WAV 아닌 파일 등) |
| 500 | 서버 오류 (STT 실패, LLM 오류 등) |

### 에러 응답 예시
```json
{
  "detail": "WAV 파일만 지원합니다 (16kHz, mono, 16bit)"
}
```

---

## OCR 팀과의 통합

OCR 팀도 동일한 JSON 스키마 사용:
```json
{
  "medication_name": "String 또는 null",
  "total_duration_days": "Integer 또는 null",
  "daily_frequency": "Integer 또는 null",
  "meal_context": "pre_meal|post_meal|at_bedtime 또는 null",
  "specific_offset_minutes": "Integer 또는 null",
  "special_instructions": "String 또는 null"
}
```

Flutter에서 OCR과 STT 결과를 동일한 `MedicationData` 모델로 처리 가능.

---

## 서버 배포 시 주의사항

1. **CORS**: 현재 `allow_origins=["*"]`로 설정됨. 프로덕션에서는 특정 도메인으로 제한 권장.

2. **환경변수**: `.env` 파일은 git에 포함하지 않음. 배포 시 환경변수 별도 설정 필요.

3. **포트**: 기본 8000번 포트 사용. 방화벽 설정 확인.

4. **HTTPS**: 프로덕션에서는 HTTPS 사용 권장 (Azure App Service 또는 Nginx 리버스 프록시).

---

## 문의

- 백엔드 담당: STT + LLM 파이프라인
- 프론트엔드(Flutter): 음성 녹음 + API 호출 + 알람 UI
- OCR 담당: 처방전 이미지 → 동일 JSON 스키마

---

*Last Updated: 2025-11-27*
