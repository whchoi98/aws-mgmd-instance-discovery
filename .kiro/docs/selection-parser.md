# 선택 파서 동작 방식

`parse_selection(sel, items)` 함수는 사용자 입력을 파싱하여 항목을 선택한다.

## 입력 형식

| 입력 | 동작 | 예시 |
|------|------|------|
| `all` | 전체 선택 | `all` → 모든 항목 |
| 알파벳 포함 | 패턴 매칭 (대소문자 무시) | `r5` → r5가 포함된 항목 |
| 숫자 쉼표 | 개별 번호 선택 | `1,3,5` → 1, 3, 5번 항목 |
| 숫자 하이픈 | 범위 선택 | `1-5` → 1~5번 항목 |
| 혼합 | 번호+범위 조합 | `1,3-5,8` → 1, 3, 4, 5, 8번 항목 |

## 서비스별 인스턴스 접두사

- RDS/Aurora/Neptune/DocumentDB: `db.` (예: `db.r5.large`)
- ElastiCache: `cache.` (예: `cache.r7g.large`)
- OpenSearch: 접두사 없음, `.search` 접미사 (예: `r7g.large.search`)
- Redshift: 접두사 없음 (예: `ra3.xlplus`)
- MemoryDB: `db.` (예: `db.r7g.large`)
