## 설치 및 실행

### 1. 의존성 설치

아래 명령어로 프로젝트의 모든 의존성을 설치합니다.

```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. API 문서
```
Swagger UI: http://127.0.0.1:8080/docs
```