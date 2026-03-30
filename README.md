# AWS Managed Service Instance Discovery

🌐 [English](#english) | [한국어](#한국어)

---

## English

CLI tool to check instance type availability for AWS managed services without creating actual resources.

### Supported Services

- RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- Aurora (MySQL, PostgreSQL)
- ElastiCache
- OpenSearch
- Neptune
- DocumentDB
- Redshift
- MemoryDB

### Usage

#### Interactive Shell (All Services)
```bash
python3 interactive.py
```

#### CLI Mode (RDS Only)
```bash
# Full discovery + batch check
python3 discovery.py --all

# Pattern filtering
python3 discovery.py --filter r5 --all

# Specify instance types directly
python3 discovery.py --classes db.r5.large db.r6g.large

# Change engine/version/region
python3 discovery.py --engine postgres --version 16.4 --region us-east-1
```

### Requirements

- Python 3.9+
- boto3
- AWS credentials (read-only Describe/List APIs only, no cost)

---

## 한국어

AWS 매니지드 서비스의 인스턴스 타입 가용성을 실제 리소스를 생성하지 않고 확인하는 CLI 도구.

### 지원 서비스

- RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- Aurora (MySQL, PostgreSQL)
- ElastiCache
- OpenSearch
- Neptune
- DocumentDB
- Redshift
- MemoryDB

### 사용법

#### 인터랙티브 셸 (전체 서비스)
```bash
python3 interactive.py
```

#### CLI 모드 (RDS 전용)
```bash
# 전체 디스커버리 + 일괄 확인
python3 discovery.py --all

# 패턴 필터링
python3 discovery.py --filter r5 --all

# 직접 지정
python3 discovery.py --classes db.r5.large db.r6g.large

# 엔진/버전/리전 변경
python3 discovery.py --engine postgres --version 16.4 --region us-east-1
```

### 요구사항

- Python 3.9+
- boto3
- AWS 자격 증명 (읽기 전용 Describe/List API만 사용, 비용 없음)
