# Steering Rules

## Code Style
- 모든 AWS API 호출에 예외 처리(try/except) 필수
- paginated 응답은 반드시 boto3 paginator 사용
- 새 서비스 추가 시 `{service}_discover()`, `{service}_check(classes)` 함수 쌍으로 구현
- 새 서비스 핸들러는 `SERVICE_HANDLERS` 딕셔너리에 등록

## Safety
- 읽기 전용 Describe/List API만 사용할 것
- Create, Delete, Modify, Put, Update 등 쓰기 API 사용 금지
- AWS 자격 증명을 코드에 하드코딩하지 않을 것

## UX
- 사용자 입력에 기본값 제공 (prompt 함수의 default 파라미터)
- 인스턴스 선택 시 번호, 범위(1-5), 패턴(r5), all 모두 지원
- 결과 출력 시 AZ 정보 포함 (가능한 서비스에 한해)
- 한국어 UI 유지

## Testing
- 자동 테스트 시 printf 파이프로 stdin 입력 시뮬레이션
- stderr의 boto3 deprecation 경고는 무시 가능
