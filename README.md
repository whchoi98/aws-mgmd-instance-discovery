# AWS Managed Service Instance Discovery

🌐 [English](#english) | [한국어](#한국어)

---

## English

A CLI tool to check instance type availability for AWS managed services **without creating actual resources**. Uses read-only AWS Describe/List APIs only — completely free, no cost incurred.

### Why This Tool?

When planning AWS infrastructure, you often need to know:
- Which instance types are available for a specific engine version?
- Which Availability Zones support a particular instance type?
- What's the difference in instance availability between RDS and Aurora?

This tool answers all of these questions instantly, without provisioning any resources.

### Supported Services

| Service | Engine/Version Selection | AZ Info |
|---------|:---:|:---:|
| RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | ✅ | ✅ |
| Aurora (MySQL, PostgreSQL) | ✅ | ✅ |
| Neptune | ✅ | ✅ |
| DocumentDB | ✅ | ✅ |
| OpenSearch | ✅ | ❌ |
| ElastiCache | ❌ | ❌ |
| Redshift | ❌ | ✅ |
| MemoryDB | ❌ | ❌ |

### Getting Started

#### Prerequisites

- Python 3.9+
- boto3 (`pip install boto3`)
- AWS credentials configured (`aws configure` or IAM role)
  - Only requires read-only permissions: `Describe*`, `List*` APIs
  - No write permissions needed — no resources are created or modified

#### Interactive Shell (Recommended)

Supports all 8 services with a menu-driven interface:

```bash
python3 interactive.py
```

**Workflow:**
1. Select a service (RDS, Aurora, ElastiCache, etc.)
2. Choose engine and version (if applicable)
3. Discover available instance types
4. Select instances to check — by number (`1,3,5`), range (`1-5`), pattern (`r5`), or `all`
5. View availability with AZ details

**Example session:**
```
============================================================
  AWS 매니지드 서비스 인스턴스 가용성 디스커버리
============================================================
  리전: ap-northeast-2

  0. 서비스 선택  (미선택)
  3. 인스턴스 디스커버리
  4. 선택 확인 (번호/패턴/all)
  5. 직접 입력 확인
  6. 리전 변경  (ap-northeast-2)
  7. 현재 설정
  q. 종료
```

#### CLI Mode (RDS Only)

For scripting and quick one-off checks:

```bash
# Discover all instance types and batch check
python3 discovery.py --all

# Filter by instance family pattern
python3 discovery.py --filter r5 --all

# Check specific instance types directly
python3 discovery.py --classes db.r5.large db.r6g.large db.m7g.xlarge

# Change engine, version, and region
python3 discovery.py --engine postgres --version 16.4 --region us-east-1

# Interactive selection after discovery
python3 discovery.py
```

### Selection Methods

When selecting instance types, you can use:

| Input | Action | Example |
|-------|--------|---------|
| `all` | Select all discovered instances | `all` |
| Pattern | Filter by name (case-insensitive) | `r5`, `m6g`, `t4g` |
| Numbers | Select by index | `1,3,5` |
| Range | Select a range | `1-5` |
| Mixed | Combine numbers and ranges | `1,3-5,8` |

### AWS APIs Used

All APIs are read-only and free of charge:

| Service | API |
|---------|-----|
| RDS / Aurora / Neptune / DocumentDB | `DescribeOrderableDBInstanceOptions`, `DescribeDBEngineVersions` |
| ElastiCache | `DescribeReservedCacheNodesOfferings` |
| OpenSearch | `ListVersions`, `ListInstanceTypeDetails` |
| Redshift | `DescribeOrderableClusterOptions` |
| MemoryDB | `DescribeReservedNodesOfferings` |

### Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeOrderableDBInstanceOptions",
        "rds:DescribeDBEngineVersions",
        "elasticache:DescribeReservedCacheNodesOfferings",
        "es:ListVersions",
        "es:ListInstanceTypeDetails",
        "redshift:DescribeOrderableClusterOptions",
        "memorydb:DescribeReservedNodesOfferings"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 한국어

AWS 매니지드 서비스의 인스턴스 타입 가용성을 **실제 리소스를 생성하지 않고** 확인하는 CLI 도구. 읽기 전용 AWS Describe/List API만 사용하며, 비용이 전혀 발생하지 않습니다.

### 왜 이 도구가 필요한가요?

AWS 인프라를 계획할 때 자주 궁금한 것들:
- 특정 엔진 버전에서 어떤 인스턴스 타입을 사용할 수 있는지?
- 특정 인스턴스 타입이 어떤 가용 영역(AZ)에서 지원되는지?
- RDS와 Aurora 간 인스턴스 가용성 차이는 무엇인지?

이 도구는 리소스를 프로비저닝하지 않고 이 모든 질문에 즉시 답합니다.

### 지원 서비스

| 서비스 | 엔진/버전 선택 | AZ 정보 |
|--------|:---:|:---:|
| RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | ✅ | ✅ |
| Aurora (MySQL, PostgreSQL) | ✅ | ✅ |
| Neptune | ✅ | ✅ |
| DocumentDB | ✅ | ✅ |
| OpenSearch | ✅ | ❌ |
| ElastiCache | ❌ | ❌ |
| Redshift | ❌ | ✅ |
| MemoryDB | ❌ | ❌ |

### 시작하기

#### 사전 요구사항

- Python 3.9+
- boto3 (`pip install boto3`)
- AWS 자격 증명 설정 (`aws configure` 또는 IAM 역할)
  - 읽기 전용 권한만 필요: `Describe*`, `List*` API
  - 쓰기 권한 불필요 — 리소스를 생성하거나 수정하지 않음

#### 인터랙티브 셸 (권장)

8개 서비스를 모두 지원하는 메뉴 기반 인터페이스:

```bash
python3 interactive.py
```

**사용 흐름:**
1. 서비스 선택 (RDS, Aurora, ElastiCache 등)
2. 엔진 및 버전 선택 (해당되는 경우)
3. 사용 가능한 인스턴스 타입 디스커버리
4. 확인할 인스턴스 선택 — 번호(`1,3,5`), 범위(`1-5`), 패턴(`r5`), `all`
5. AZ 상세 정보와 함께 가용성 확인

**실행 예시:**
```
============================================================
  AWS 매니지드 서비스 인스턴스 가용성 디스커버리
============================================================
  리전: ap-northeast-2

  0. 서비스 선택  (미선택)
  3. 인스턴스 디스커버리
  4. 선택 확인 (번호/패턴/all)
  5. 직접 입력 확인
  6. 리전 변경  (ap-northeast-2)
  7. 현재 설정
  q. 종료
```

#### CLI 모드 (RDS 전용)

스크립팅 및 빠른 일회성 확인용:

```bash
# 전체 인스턴스 타입 디스커버리 + 일괄 확인
python3 discovery.py --all

# 인스턴스 패밀리 패턴 필터링
python3 discovery.py --filter r5 --all

# 특정 인스턴스 타입 직접 확인
python3 discovery.py --classes db.r5.large db.r6g.large db.m7g.xlarge

# 엔진, 버전, 리전 변경
python3 discovery.py --engine postgres --version 16.4 --region us-east-1

# 디스커버리 후 대화형 선택
python3 discovery.py
```

### 선택 방법

인스턴스 타입 선택 시 다양한 입력 방식을 지원합니다:

| 입력 | 동작 | 예시 |
|------|------|------|
| `all` | 전체 선택 | `all` |
| 패턴 | 이름으로 필터링 (대소문자 무시) | `r5`, `m6g`, `t4g` |
| 번호 | 인덱스로 선택 | `1,3,5` |
| 범위 | 범위 선택 | `1-5` |
| 혼합 | 번호와 범위 조합 | `1,3-5,8` |

### 사용되는 AWS API

모든 API는 읽기 전용이며 무료입니다:

| 서비스 | API |
|--------|-----|
| RDS / Aurora / Neptune / DocumentDB | `DescribeOrderableDBInstanceOptions`, `DescribeDBEngineVersions` |
| ElastiCache | `DescribeReservedCacheNodesOfferings` |
| OpenSearch | `ListVersions`, `ListInstanceTypeDetails` |
| Redshift | `DescribeOrderableClusterOptions` |
| MemoryDB | `DescribeReservedNodesOfferings` |

### 필요한 IAM 권한

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeOrderableDBInstanceOptions",
        "rds:DescribeDBEngineVersions",
        "elasticache:DescribeReservedCacheNodesOfferings",
        "es:ListVersions",
        "es:ListInstanceTypeDetails",
        "redshift:DescribeOrderableClusterOptions",
        "memorydb:DescribeReservedNodesOfferings"
      ],
      "Resource": "*"
    }
  ]
}
```
