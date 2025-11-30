"""
설정 및 데이터 테스트 스크립트

프로젝트가 올바르게 설정되었는지 확인합니다.
"""

import os
import sys
import pandas as pd

sys.path.append('/Volumes/T7/class/2025-FALL/big_data')


def test_data_files():
    """데이터 파일 존재 여부 확인"""
    print("=" * 60)
    print("데이터 파일 확인")
    print("=" * 60)
    
    data_dir = '/Volumes/T7/class/2025-FALL/big_data/data'
    required_files = [
        'whale_transactions_rows_ETH_rev1.csv',
        'price_history_eth_rows.csv',
        'price_history_btc_rows.csv'
    ]
    
    optional_files = [
        'telegram_data.csv',
        'processed_data.csv',
        'alert_history.csv'
    ]
    
    print("\n필수 파일:")
    all_required_exist = True
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file}")
        if not exists:
            all_required_exist = False
    
    print("\n선택 파일:")
    for file in optional_files:
        file_path = os.path.join(data_dir, file)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "⚠️ "
        print(f"  {status} {file}")
    
    return all_required_exist


def test_imports():
    """패키지 임포트 테스트"""
    print("\n" + "=" * 60)
    print("패키지 임포트 테스트")
    print("=" * 60)
    
    tests = []
    
    # 데이터 로더
    try:
        from utils.data_loader import DataLoader
        print("  ✅ utils.data_loader")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ utils.data_loader: {e}")
        tests.append(False)
    
    # 상관관계 분석
    try:
        from analysis.correlation_analysis import CorrelationAnalyzer
        print("  ✅ analysis.correlation_analysis")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ analysis.correlation_analysis: {e}")
        tests.append(False)
    
    # 스파이크 감지
    try:
        from analysis.spike_detector import SpikeDetector
        print("  ✅ analysis.spike_detector")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ analysis.spike_detector: {e}")
        tests.append(False)
    
    # 알람 시스템
    try:
        from utils.alert_system import AlertSystem
        print("  ✅ utils.alert_system")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ utils.alert_system: {e}")
        tests.append(False)
    
    # 컴포넌트
    try:
        from components import charts, metrics, filters, alerts
        print("  ✅ components")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ components: {e}")
        tests.append(False)
    
    return all(tests)


def test_data_loading():
    """데이터 로딩 테스트"""
    print("\n" + "=" * 60)
    print("데이터 로딩 테스트")
    print("=" * 60)
    
    try:
        from utils.data_loader import DataLoader
        
        loader = DataLoader()
        
        # 고래 거래 데이터
        whale_tx = loader.load_whale_transactions()
        print(f"\n  ✅ 고래 거래 데이터: {len(whale_tx):,} 행")
        
        # ETH 가격 데이터
        eth_price = loader.load_price_data('ETH')
        print(f"  ✅ ETH 가격 데이터: {len(eth_price):,} 행")
        
        # BTC 가격 데이터
        btc_price = loader.load_price_data('BTC')
        print(f"  ✅ BTC 가격 데이터: {len(btc_price):,} 행")
        
        # 텔레그램 데이터 (선택)
        telegram_data = loader.load_telegram_data()
        if not telegram_data.empty:
            print(f"  ✅ 텔레그램 데이터: {len(telegram_data):,} 행")
        else:
            print(f"  ⚠️  텔레그램 데이터: 없음 (아직 수집 전)")
        
        return True
    
    except Exception as e:
        print(f"  ❌ 데이터 로딩 실패: {e}")
        return False


def test_processed_data():
    """전처리된 데이터 확인"""
    print("\n" + "=" * 60)
    print("전처리된 데이터 확인")
    print("=" * 60)
    
    processed_file = '/Volumes/T7/class/2025-FALL/big_data/data/processed_data.csv'
    
    if not os.path.exists(processed_file):
        print("  ⚠️  전처리된 데이터 파일이 없습니다.")
        print("  ℹ️  다음 명령어로 생성하세요: python scripts/preprocess_data.py")
        return False
    
    try:
        df = pd.read_csv(processed_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"\n  ✅ 데이터 로드 성공")
        print(f"  📊 행 수: {len(df):,}")
        print(f"  📋 컬럼 수: {len(df.columns)}")
        print(f"  📅 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
        
        # 주요 컬럼 확인
        key_columns = ['ETH_close', 'BTC_close', 'tx_frequency', 'message_count']
        print(f"\n  주요 컬럼:")
        for col in key_columns:
            if col in df.columns:
                print(f"    ✅ {col}")
            else:
                print(f"    ❌ {col} (없음)")
        
        return True
    
    except Exception as e:
        print(f"  ❌ 데이터 로드 실패: {e}")
        return False


def test_environment():
    """환경 변수 확인"""
    print("\n" + "=" * 60)
    print("환경 변수 확인")
    print("=" * 60)
    
    env_file = '/Volumes/T7/class/2025-FALL/big_data/.env'
    
    if not os.path.exists(env_file):
        print("  ⚠️  .env 파일이 없습니다.")
        print("  ℹ️  텔레그램 데이터 수집을 위해 .env 파일을 생성하세요.")
        print("  ℹ️  env.example 파일을 참고하세요.")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        phone = os.getenv('TELEGRAM_PHONE')
        
        if api_id and api_hash and phone:
            print(f"  ✅ Telegram API 설정 완료")
            print(f"    - API ID: {'*' * len(api_id)}")
            print(f"    - API Hash: {'*' * 8}...")
            print(f"    - Phone: {phone[:5]}***")
            return True
        else:
            print(f"  ⚠️  일부 환경 변수가 설정되지 않았습니다.")
            if not api_id:
                print("    ❌ TELEGRAM_API_ID")
            if not api_hash:
                print("    ❌ TELEGRAM_API_HASH")
            if not phone:
                print("    ❌ TELEGRAM_PHONE")
            return False
    
    except Exception as e:
        print(f"  ❌ 환경 변수 로드 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "프로젝트 설정 및 테스트" + " " * 25 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 테스트 실행
    results.append(("데이터 파일", test_data_files()))
    results.append(("패키지 임포트", test_imports()))
    results.append(("데이터 로딩", test_data_loading()))
    results.append(("전처리된 데이터", test_processed_data()))
    results.append(("환경 변수", test_environment()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"  {status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\n  총 {total_passed}/{total_tests} 테스트 통과")
    
    if total_passed == total_tests:
        print("\n  🎉 모든 테스트를 통과했습니다!")
        print("  ℹ️  다음 명령어로 대시보드를 실행하세요:")
        print("      streamlit run app.py")
    else:
        print("\n  ⚠️  일부 테스트가 실패했습니다.")
        print("  ℹ️  README.md 파일을 참고하여 설정을 완료하세요.")
    
    print()


if __name__ == '__main__':
    main()

