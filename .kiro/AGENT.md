# Agent Instructions for aws-mgmd-instance-discovery

## Project Overview

AWS 매니지드 서비스(RDS, Aurora, ElastiCache, OpenSearch, Neptune, DocumentDB, Redshift, MemoryDB)의 인스턴스 타입 가용성을 조회하는 Python CLI 도구. 읽기 전용 AWS Describe/List API만 사용하며 비용이 발생하지 않는다.

## Architecture

- `discovery.py` — RDS 전용 CLI 도구 (argparse 기반, 비대화형/대화형 모드)
- `interactive.py` — 전체 서비스 통합 인터랙티브 셸 (메뉴 기반)

### 핵심 패턴

각 서비스는 동일한 3단계 패턴을 따른다:
1. **Discover** — 사용 가능한 인스턴스 타입 목록 조회
2. **Select** — 번호, 범위, 패턴, all 중 선택
3. **Check** — 선택된 인스턴스의 AZ별 가용성 확인

서비스별 핸들러는 `SERVICE_HANDLERS` 딕셔너리에 매핑되어 있으며, `discover`, `check`, `has_engine` 키를 가진다.

### AWS API 매핑

| 서비스 | Discover API | 비고 |
|--------|-------------|------|
| RDS/Aurora/Neptune/DocumentDB | `describe_orderable_db_instance_options` | 엔진+버전 필수 |
| ElastiCache | `describe_reserved_cache_nodes_offerings` | 버전 불필요 |
| OpenSearch | `list_instance_type_details` | 엔진 버전 필수 |
| Redshift | `describe_orderable_cluster_options` | 버전 불필요 |
| MemoryDB | `describe_reserved_nodes_offerings` | 버전 불필요 |

## Coding Conventions

- Python 3.9+ 호환
- boto3 paginator 사용 (paginated 응답 처리)
- 전역 상태: `region`, `clients`, `cached_classes`, `current_service`, `current_engine`, `current_version`
- 한국어 UI 출력
- 함수명: `{service}_{action}` 패턴 (예: `rds_discover`, `elasticache_check`)

## Key Constraints

- 읽기 전용 API만 사용 — 리소스 생성/수정/삭제 절대 금지
- API Rate Limit 주의 — 반복 호출 시 적절한 간격 유지
- Neptune/DocumentDB는 RDS API를 공유하므로 엔진명만 다르게 전달
