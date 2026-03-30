#!/usr/bin/env python3
"""설치 환경 사전 체크"""

import sys
import shutil


def check():
    ok = True

    # Python 버전
    v = sys.version_info
    if v >= (3, 9):
        print(f"  ✅ Python {v.major}.{v.minor}.{v.micro}")
    else:
        print(f"  ❌ Python {v.major}.{v.minor}.{v.micro} (3.9+ 필요)")
        ok = False

    # boto3
    try:
        import boto3
        print(f"  ✅ boto3 {boto3.__version__}")
    except ImportError:
        print("  ❌ boto3 미설치 → pip install boto3")
        ok = False

    # AWS 자격 증명
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"  ✅ AWS 자격 증명 (Account: {identity['Account']})")
    except Exception as e:
        print(f"  ❌ AWS 자격 증명 실패 → aws configure 필요")
        ok = False

    # AWS CLI (선택)
    if shutil.which('aws'):
        import subprocess
        ver = subprocess.run(['aws', '--version'], capture_output=True, text=True).stdout.strip()
        print(f"  ✅ {ver}")
    else:
        print("  ⚠️  AWS CLI 미설치 (선택사항)")

    print()
    if ok:
        print("  ✅ 모든 필수 요구사항 충족. 바로 사용 가능합니다.")
        print("     → python3 interactive.py")
    else:
        print("  ❌ 필수 요구사항을 확인하세요.")
    return ok


if __name__ == '__main__':
    print("\n  환경 체크\n")
    sys.exit(0 if check() else 1)
