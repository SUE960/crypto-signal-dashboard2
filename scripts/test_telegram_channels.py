"""
텔레그램 채널 접근 테스트

어떤 채널에 접근 가능한지 확인합니다.
"""

import os
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
PHONE = os.getenv('TELEGRAM_PHONE')

# 테스트할 채널 목록 (암호화폐 관련 주요 채널들)
TEST_CHANNELS = [
    # 현재 사용 중
    '@whale_alert',      # 고래 거래 알림 (프로젝트 핵심!)
    '@cointelegraph',    # 뉴스
    '@bitcoin',          # 비트코인 커뮤니티
    
    # 거래소 관련
    '@binance',          # 바이낸스 공식
    '@BinanceKorean',    # 바이낸스 한국
    '@coinbase',         # 코인베이스
    '@Bybit_Official',   # 바이빗
    '@krakenfx',         # 크라켄
    
    # 주요 암호화폐 프로젝트
    '@ethereum',         # 이더리움
    '@Cardano',          # 카르다노
    '@SolanaNews',       # 솔라나
    '@Polkadot',         # 폴카닷
    
    # 뉴스 및 분석
    '@CryptoNews',       # 암호화폐 뉴스
    '@bitcoinmagazine',  # 비트코인 매거진
    '@decryptmedia',     # Decrypt 미디어
    '@coindesk',         # CoinDesk
    
    # 커뮤니티 및 트레이딩
    '@cryptosignals',    # 크립토 시그널
    '@CryptoWhales',     # 크립토 고래들
    '@AltcoinDaily',     # 알트코인 데일리
    '@CryptoGodJohn',    # 유명 크립토 분석가
]


async def test_channel_access():
    """채널 접근 테스트"""
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    await client.start(phone=PHONE)
    print("✓ Telegram 로그인 성공!\n")
    
    print("=" * 60)
    print("채널 접근 테스트")
    print("=" * 60)
    
    working_channels = []
    
    for channel in TEST_CHANNELS:
        try:
            # 채널 정보 가져오기
            entity = await client.get_entity(channel)
            
            # 최근 메시지 1개만 가져와서 테스트
            messages = await client.get_messages(entity, limit=1)
            
            if messages:
                msg = messages[0]
                print(f"✅ {channel}")
                print(f"   제목: {entity.title if hasattr(entity, 'title') else '제목없음'}")
                print(f"   멤버: {entity.participants_count if hasattr(entity, 'participants_count') else '알 수 없음'}")
                print(f"   최근 메시지: {msg.date}")
                print(f"   메시지 읽기: 가능")
                working_channels.append(channel)
            else:
                print(f"⚠️  {channel} - 채널은 찾았으나 메시지가 없음")
            
            print()
            
        except Exception as e:
            print(f"❌ {channel} - 접근 불가")
            print(f"   오류: {e}")
            print()
    
    await client.disconnect()
    
    print("=" * 60)
    print(f"접근 가능한 채널: {len(working_channels)}개")
    print("=" * 60)
    
    if working_channels:
        print("\n✅ 사용 가능한 채널:")
        for ch in working_channels:
            print(f"  - {ch}")
        
        # .env 파일 업데이트 제안
        print(f"\n💡 .env 파일의 TELEGRAM_CHANNELS를 다음으로 변경하세요:")
        print(f"   TELEGRAM_CHANNELS={','.join(working_channels)}")
    else:
        print("\n⚠️  접근 가능한 채널이 없습니다.")
        print("   공개 채널이거나 본인이 가입한 채널이어야 합니다.")


if __name__ == '__main__':
    asyncio.run(test_channel_access())

