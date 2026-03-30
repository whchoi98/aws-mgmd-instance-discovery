#!/usr/bin/env python3
"""AWS 매니지드 서비스 인스턴스 가용성 인터랙티브 셸"""

import boto3
import sys
from datetime import datetime

region = 'ap-northeast-2'
clients = {}
cached_classes = []
current_service = None
current_engine = None
current_version = None


# ── 서비스 정의 ──────────────────────────────────────────

SERVICES = {
    '1': 'RDS / Aurora',
    '2': 'ElastiCache',
    '3': 'OpenSearch',
    '4': 'Neptune',
    '5': 'DocumentDB',
    '6': 'Redshift',
    '7': 'MemoryDB',
}

RDS_ENGINES = {
    '1': ('mysql', 'RDS MySQL'),
    '2': ('postgres', 'RDS PostgreSQL'),
    '3': ('aurora-mysql', 'Aurora MySQL'),
    '4': ('aurora-postgresql', 'Aurora PostgreSQL'),
    '5': ('mariadb', 'RDS MariaDB'),
    '6': ('oracle-ee', 'RDS Oracle EE'),
    '7': ('sqlserver-ee', 'RDS SQL Server EE'),
    '8': ('neptune', 'Neptune'),
    '9': ('docdb', 'DocumentDB'),
}


def get_client(service):
    if service not in clients:
        clients[service] = boto3.client(service, region_name=region)
    return clients[service]


def prompt(msg, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val or default


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def parse_selection(sel, items):
    """번호/범위/패턴/all 파싱"""
    if sel.lower() == 'all':
        return items
    if any(c.isalpha() for c in sel):
        return [c for c in items if sel.lower() in c.lower()]
    indices = set()
    for part in sel.split(','):
        part = part.strip()
        if '-' in part:
            s, e = part.split('-', 1)
            indices.update(range(int(s), int(e) + 1))
        else:
            indices.add(int(part))
    return [items[i - 1] for i in sorted(indices) if 1 <= i <= len(items)]


def print_list(items, label="항목"):
    print(f"\n총 {len(items)}개 {label}:\n")
    for i, c in enumerate(items, 1):
        print(f"  {i:3d}. {c}")


# ── RDS / Aurora / Neptune / DocumentDB ──────────────────

def rds_select_engine():
    global current_engine, current_version, cached_classes
    print_header("DB 엔진 선택")
    for k, (_, label) in RDS_ENGINES.items():
        print(f"  {k}. {label}")
    sel = prompt("\n번호 선택", '1')
    if sel not in RDS_ENGINES:
        print("잘못된 선택입니다.")
        return
    current_engine = RDS_ENGINES[sel]
    current_version = None
    cached_classes = []
    print(f"\n→ {current_engine[1]} 선택됨")


def rds_select_version():
    global current_version, cached_classes
    if not current_engine:
        print("먼저 엔진을 선택하세요.")
        return
    print_header(f"{current_engine[1]} 사용 가능한 버전")
    try:
        rds = get_client('rds')
        resp = rds.describe_db_engine_versions(Engine=current_engine[0])
        versions = [v['EngineVersion'] for v in resp['DBEngineVersions']]
        if not versions:
            print("사용 가능한 버전이 없습니다.")
            return
        for i, v in enumerate(versions, 1):
            print(f"  {i:3d}. {v}")
        sel = prompt(f"\n번호 또는 버전 직접 입력", str(len(versions)))
        if sel.isdigit() and 1 <= int(sel) <= len(versions):
            current_version = versions[int(sel) - 1]
        else:
            current_version = sel
        cached_classes = []
        print(f"\n→ {current_engine[1]} {current_version} 선택됨")
    except Exception as e:
        print(f"오류: {e}")


def rds_discover():
    global cached_classes
    if not current_version:
        print("먼저 엔진과 버전을 선택하세요.")
        return
    print_header(f"{current_engine[1]} {current_version} 인스턴스 디스커버리")
    try:
        rds = get_client('rds')
        paginator = rds.get_paginator('describe_orderable_db_instance_options')
        options = []
        for page in paginator.paginate(Engine=current_engine[0], EngineVersion=current_version):
            options.extend(page['OrderableDBInstanceOptions'])
        cached_classes = sorted({o['DBInstanceClass'] for o in options})
        print_list(cached_classes, "인스턴스 타입")
    except Exception as e:
        print(f"오류: {e}")


def rds_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] {current_engine[1]} {current_version} 가용성 확인\n")
    print(f"  {'인스턴스 타입':<25} {'상태':<10} {'AZ'}")
    print(f"  {'-'*25} {'-'*10} {'-'*40}")
    rds = get_client('rds')
    paginator = rds.get_paginator('describe_orderable_db_instance_options')
    for cls in classes:
        try:
            options = []
            for page in paginator.paginate(Engine=current_engine[0], EngineVersion=current_version, DBInstanceClass=cls):
                options.extend(page['OrderableDBInstanceOptions'])
            if options:
                azs = sorted({az['Name'] for o in options for az in o['AvailabilityZones']})
                print(f"  {cls:<25} {'✅ 가능':<10} {', '.join(azs)}")
            else:
                print(f"  {cls:<25} {'❌ 불가':<10}")
        except Exception as e:
            print(f"  {cls:<25} {'⚠️ 오류':<10} {e}")


# ── ElastiCache ──────────────────────────────────────────

def elasticache_discover():
    global cached_classes, current_engine, current_version
    print_header("ElastiCache 인스턴스 디스커버리")
    current_engine = ('elasticache', 'ElastiCache')
    current_version = 'N/A'
    try:
        ec = get_client('elasticache')
        paginator = ec.get_paginator('describe_reserved_cache_nodes_offerings')
        types = set()
        for page in paginator.paginate():
            for o in page['ReservedCacheNodesOfferings']:
                types.add(o['CacheNodeType'])
        cached_classes = sorted(types)
        print_list(cached_classes, "노드 타입")
    except Exception as e:
        print(f"오류: {e}")


def elasticache_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] ElastiCache 가용성 확인\n")
    print(f"  {'노드 타입':<25} {'상태':<10}")
    print(f"  {'-'*25} {'-'*10}")
    ec = get_client('elasticache')
    paginator = ec.get_paginator('describe_reserved_cache_nodes_offerings')
    all_types = set()
    for page in paginator.paginate():
        for o in page['ReservedCacheNodesOfferings']:
            all_types.add(o['CacheNodeType'])
    for cls in classes:
        status = '✅ 가능' if cls in all_types else '❌ 불가'
        print(f"  {cls:<25} {status:<10}")


# ── OpenSearch ───────────────────────────────────────────

def opensearch_discover():
    global cached_classes, current_engine, current_version
    print_header("OpenSearch 버전 선택")
    try:
        os_client = get_client('opensearch')
        resp = os_client.list_versions()
        versions = resp['Versions']
        for i, v in enumerate(versions, 1):
            print(f"  {i:3d}. {v}")
        sel = prompt("\n번호 선택", str(len(versions)))
        if sel.isdigit() and 1 <= int(sel) <= len(versions):
            ver = versions[int(sel) - 1]
        else:
            ver = sel
        current_engine = ('opensearch', 'OpenSearch')
        current_version = ver
        print_header(f"OpenSearch {ver} 인스턴스 디스커버리")
        resp = os_client.list_instance_type_details(EngineVersion=ver)
        cached_classes = sorted([t['InstanceType'] for t in resp['InstanceTypeDetails']])
        print_list(cached_classes, "인스턴스 타입")
    except Exception as e:
        print(f"오류: {e}")


def opensearch_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] OpenSearch {current_version} 가용성 확인\n")
    print(f"  {'인스턴스 타입':<35} {'상태':<10}")
    print(f"  {'-'*35} {'-'*10}")
    os_client = get_client('opensearch')
    resp = os_client.list_instance_type_details(EngineVersion=current_version)
    available = {t['InstanceType'] for t in resp['InstanceTypeDetails']}
    for cls in classes:
        status = '✅ 가능' if cls in available else '❌ 불가'
        print(f"  {cls:<35} {status:<10}")


# ── Redshift ─────────────────────────────────────────────

def redshift_discover():
    global cached_classes, current_engine, current_version
    print_header("Redshift 노드 타입 디스커버리")
    current_engine = ('redshift', 'Redshift')
    current_version = 'N/A'
    try:
        rs = get_client('redshift')
        paginator = rs.get_paginator('describe_orderable_cluster_options')
        types = set()
        for page in paginator.paginate():
            for o in page['OrderableClusterOptions']:
                types.add(o['NodeType'])
        cached_classes = sorted(types)
        print_list(cached_classes, "노드 타입")
    except Exception as e:
        print(f"오류: {e}")


def redshift_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] Redshift 가용성 확인\n")
    print(f"  {'노드 타입':<25} {'상태':<10} {'AZ'}")
    print(f"  {'-'*25} {'-'*10} {'-'*40}")
    rs = get_client('redshift')
    paginator = rs.get_paginator('describe_orderable_cluster_options')
    for cls in classes:
        try:
            options = []
            for page in paginator.paginate(NodeType=cls):
                options.extend(page['OrderableClusterOptions'])
            if options:
                azs = sorted({az['Name'] for o in options for az in o['AvailabilityZones']})
                print(f"  {cls:<25} {'✅ 가능':<10} {', '.join(azs)}")
            else:
                print(f"  {cls:<25} {'❌ 불가':<10}")
        except Exception as e:
            print(f"  {cls:<25} {'⚠️ 오류':<10} {e}")


# ── MemoryDB ─────────────────────────────────────────────

def memorydb_discover():
    global cached_classes, current_engine, current_version
    print_header("MemoryDB 노드 타입 디스커버리")
    current_engine = ('memorydb', 'MemoryDB')
    current_version = 'N/A'
    try:
        mdb = get_client('memorydb')
        resp = mdb.describe_reserved_nodes_offerings()
        types = sorted({o['NodeType'] for o in resp['ReservedNodesOfferings']})
        cached_classes = types
        print_list(cached_classes, "노드 타입")
    except Exception as e:
        print(f"오류: {e}")


def memorydb_check(classes):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] MemoryDB 가용성 확인\n")
    print(f"  {'노드 타입':<25} {'상태':<10}")
    print(f"  {'-'*25} {'-'*10}")
    mdb = get_client('memorydb')
    resp = mdb.describe_reserved_nodes_offerings()
    available = {o['NodeType'] for o in resp['ReservedNodesOfferings']}
    for cls in classes:
        status = '✅ 가능' if cls in available else '❌ 불가'
        print(f"  {cls:<25} {status:<10}")


# ── 서비스별 핸들러 매핑 ─────────────────────────────────

SERVICE_HANDLERS = {
    'RDS / Aurora': {
        'select_engine': rds_select_engine,
        'select_version': rds_select_version,
        'discover': rds_discover,
        'check': rds_check,
        'has_engine': True,
    },
    'Neptune': {
        'select_engine': lambda: _set_rds_engine('8', RDS_ENGINES),
        'select_version': rds_select_version,
        'discover': rds_discover,
        'check': rds_check,
        'has_engine': False,
    },
    'DocumentDB': {
        'select_engine': lambda: _set_rds_engine('9', RDS_ENGINES),
        'select_version': rds_select_version,
        'discover': rds_discover,
        'check': rds_check,
        'has_engine': False,
    },
    'ElastiCache': {
        'discover': elasticache_discover,
        'check': elasticache_check,
        'has_engine': False,
    },
    'OpenSearch': {
        'discover': opensearch_discover,
        'check': opensearch_check,
        'has_engine': False,
    },
    'Redshift': {
        'discover': redshift_discover,
        'check': redshift_check,
        'has_engine': False,
    },
    'MemoryDB': {
        'discover': memorydb_discover,
        'check': memorydb_check,
        'has_engine': False,
    },
}


def _set_rds_engine(key, engines):
    global current_engine, current_version, cached_classes
    current_engine = engines[key]
    current_version = None
    cached_classes = []
    print(f"\n→ {current_engine[1]} 선택됨")


# ── 메인 루프 ────────────────────────────────────────────

def select_service():
    global current_service, current_engine, current_version, cached_classes, clients
    print_header("서비스 선택")
    for k, v in SERVICES.items():
        print(f"  {k}. {v}")
    sel = prompt("\n번호 선택", '1')
    if sel not in SERVICES:
        print("잘못된 선택입니다.")
        return
    current_service = SERVICES[sel]
    current_engine = None
    current_version = None
    cached_classes = []
    clients = {}
    handler = SERVICE_HANDLERS[current_service]
    print(f"\n→ {current_service} 선택됨")
    # Neptune/DocumentDB는 엔진 자동 설정
    if 'select_engine' in handler and not handler['has_engine']:
        handler['select_engine']()


def change_region():
    global region, clients, cached_classes
    new = prompt("리전 입력", region)
    if new != region:
        region = new
        clients = {}
        cached_classes = []
    print(f"\n→ 리전: {region}")


def show_status():
    print(f"\n  리전: {region}")
    print(f"  서비스: {current_service or '미선택'}")
    eng = current_engine[1] if current_engine else '미선택'
    print(f"  엔진: {eng}")
    print(f"  버전: {current_version or '미선택'}")
    print(f"  디스커버리: {len(cached_classes)}개")


def main():
    print_header("AWS 매니지드 서비스 인스턴스 가용성 디스커버리")
    print(f"  리전: {region}")

    while True:
        print(f"\n{'─'*40}")
        print(f"  0. 서비스 선택  ({current_service or '미선택'})")
        handler = SERVICE_HANDLERS.get(current_service, {})
        if handler.get('has_engine'):
            print(f"  1. 엔진 선택")
        if 'select_version' in handler:
            print(f"  2. 버전 선택")
        print(f"  3. 인스턴스 디스커버리")
        print(f"  4. 선택 확인 (번호/패턴/all)")
        print(f"  5. 직접 입력 확인")
        print(f"  6. 리전 변경  ({region})")
        print(f"  7. 현재 설정")
        print(f"  q. 종료")

        sel = prompt("\n메뉴 선택", '').lower()

        if sel == 'q':
            print("종료합니다.")
            break
        elif sel == '0':
            select_service()
        elif sel == '1' and handler.get('has_engine'):
            handler['select_engine']()
        elif sel == '2' and 'select_version' in handler:
            handler['select_version']()
        elif sel == '3':
            if not current_service:
                print("먼저 서비스를 선택하세요. (0번)")
                continue
            handler['discover']()
        elif sel == '4':
            if not cached_classes:
                print("먼저 디스커버리를 실행하세요. (3번)")
                continue
            print("\n선택: 번호(1,3,5) | 범위(1-5) | 패턴(r5) | all")
            s = prompt("선택")
            if s:
                selected = parse_selection(s, cached_classes)
                if selected:
                    if any(c.isalpha() for c in s) and s.lower() != 'all':
                        print(f"'{s}' 패턴 매칭: {len(selected)}개")
                    handler['check'](selected)
                else:
                    print("선택된 항목이 없습니다.")
        elif sel == '5':
            if not current_service:
                print("먼저 서비스를 선택하세요. (0번)")
                continue
            val = prompt("인스턴스 타입 입력 (쉼표 구분)")
            if val:
                handler['check']([c.strip() for c in val.split(',')])
        elif sel == '6':
            change_region()
        elif sel == '7':
            show_status()
        else:
            print("잘못된 선택입니다.")


if __name__ == '__main__':
    main()
