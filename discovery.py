#!/usr/bin/env python3
"""RDS 인스턴스 타입 가용성 디스커버리 도구"""

import argparse
import sys
import boto3
from datetime import datetime


def get_orderable_options(rds, engine, engine_version, db_instance_class=None):
    """paginator로 orderable 옵션 전체 조회"""
    paginator = rds.get_paginator('describe_orderable_db_instance_options')
    params = {'Engine': engine, 'EngineVersion': engine_version}
    if db_instance_class:
        params['DBInstanceClass'] = db_instance_class
    options = []
    for page in paginator.paginate(**params):
        options.extend(page['OrderableDBInstanceOptions'])
    return options


def discover(rds, engine, engine_version):
    """사용 가능한 인스턴스 타입 목록 디스커버리"""
    options = get_orderable_options(rds, engine, engine_version)
    classes = sorted({o['DBInstanceClass'] for o in options})
    print(f"\n[{engine} {engine_version}] 사용 가능한 인스턴스 타입 ({len(classes)}개):\n")
    for i, cls in enumerate(classes, 1):
        print(f"  {i:3d}. {cls}")
    return classes


def check_classes(rds, engine, engine_version, classes):
    """인스턴스 타입별 가용성 상세 확인"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] {engine} {engine_version} 가용성 확인\n")
    print(f"  {'인스턴스 타입':<25} {'상태':<10} {'AZ'}")
    print(f"  {'-'*25} {'-'*10} {'-'*30}")
    for cls in classes:
        try:
            options = get_orderable_options(rds, engine, engine_version, cls)
            if options:
                azs = sorted({az['Name'] for o in options for az in o['AvailabilityZones']})
                print(f"  {cls:<25} {'✅ 가능':<10} {', '.join(azs)}")
            else:
                print(f"  {cls:<25} {'❌ 불가':<10}")
        except Exception as e:
            print(f"  {cls:<25} {'⚠️ 오류':<10} {e}")


def interactive_select(classes):
    """대화형 인스턴스 타입 선택"""
    print("\n선택 방법:")
    print("  - 번호 입력 (예: 1,3,5)")
    print("  - 범위 입력 (예: 1-5)")
    print("  - 패턴 입력 (예: r5, db.m6g)")
    print("  - 'all' 입력시 전체 선택")
    sel = input("\n선택: ").strip()
    if sel.lower() == 'all':
        return classes
    # 패턴 매칭
    if any(c.isalpha() for c in sel) and sel.lower() != 'all':
        return [c for c in classes if sel.lower() in c.lower()]
    # 번호/범위 파싱
    indices = set()
    for part in sel.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            indices.update(range(int(start), int(end) + 1))
        else:
            indices.add(int(part))
    return [classes[i - 1] for i in sorted(indices) if 1 <= i <= len(classes)]


def main():
    parser = argparse.ArgumentParser(description='RDS 인스턴스 타입 가용성 디스커버리')
    parser.add_argument('--engine', default='mysql', help='DB 엔진 (기본: mysql)')
    parser.add_argument('--version', default='8.4.7', help='엔진 버전 (기본: 8.4.7)')
    parser.add_argument('--region', default='ap-northeast-2', help='AWS 리전 (기본: ap-northeast-2)')
    parser.add_argument('--classes', nargs='+', help='확인할 인스턴스 타입 직접 지정')
    parser.add_argument('--all', action='store_true', help='전체 인스턴스 타입 일괄 확인')
    parser.add_argument('--filter', help='인스턴스 타입 필터 패턴 (예: r5, m6g)')
    args = parser.parse_args()

    rds = boto3.client('rds', region_name=args.region)
    print(f"리전: {args.region} | 엔진: {args.engine} {args.version}")

    # 직접 지정
    if args.classes:
        check_classes(rds, args.engine, args.version, args.classes)
        return

    # 디스커버리
    try:
        classes = discover(rds, args.engine, args.version)
    except Exception as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)

    if not classes:
        print("사용 가능한 인스턴스 타입이 없습니다.")
        return

    # 필터 적용
    if args.filter:
        classes = [c for c in classes if args.filter.lower() in c.lower()]
        print(f"\n'{args.filter}' 필터 적용: {len(classes)}개")

    # 전체 또는 대화형 선택
    if args.all:
        selected = classes
    else:
        selected = interactive_select(classes)

    if selected:
        check_classes(rds, args.engine, args.version, selected)
    else:
        print("선택된 인스턴스 타입이 없습니다.")


if __name__ == '__main__':
    main()
