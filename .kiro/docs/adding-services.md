# 서비스 추가 가이드

## 새 AWS 매니지드 서비스 추가 방법

### 1. Discover 함수 작성

```python
def newservice_discover():
    global cached_classes, current_engine, current_version
    print_header("NewService 인스턴스 디스커버리")
    current_engine = ('newservice', 'NewService')
    current_version = 'N/A'  # 버전이 필요 없는 경우
    try:
        client = get_client('newservice')
        # API 호출로 인스턴스 타입 목록 조회
        cached_classes = sorted(types)
        print_list(cached_classes, "인스턴스 타입")
    except Exception as e:
        print(f"오류: {e}")
```

### 2. Check 함수 작성

```python
def newservice_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] NewService 가용성 확인\n")
    # 각 인스턴스 타입별 가용성 출력
```

### 3. 핸들러 등록

```python
# SERVICES 딕셔너리에 추가
'8': 'NewService',

# SERVICE_HANDLERS에 추가
'NewService': {
    'discover': newservice_discover,
    'check': newservice_check,
    'has_engine': False,
},
```

## 사용되는 AWS API 목록

모두 읽기 전용이며 비용 없음:

- `rds:DescribeOrderableDBInstanceOptions`
- `rds:DescribeDBEngineVersions`
- `elasticache:DescribeReservedCacheNodesOfferings`
- `opensearch:ListVersions`
- `opensearch:ListInstanceTypeDetails`
- `redshift:DescribeOrderableClusterOptions`
- `memorydb:DescribeReservedNodesOfferings`
