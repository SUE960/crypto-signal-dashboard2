"""
코인니스 HTML 구조 디버깅 스크립트
실제로 어떤 HTML이 반환되는지 확인합니다.
"""

import requests
from bs4 import BeautifulSoup

url = 'https://coinness.com/article'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

print("코인니스 페이지 요청 중...")
response = requests.get(url, headers=headers, timeout=15)

print(f"상태 코드: {response.status_code}")
print(f"응답 길이: {len(response.text)} 바이트")
print("\n" + "=" * 60)
print("HTML 내용 미리보기 (처음 2000자):")
print("=" * 60)
print(response.text[:2000])
print("\n" + "=" * 60)

# BeautifulSoup으로 파싱
soup = BeautifulSoup(response.text, 'html.parser')

# ArticleWrapper 찾기
article_wrappers = soup.find_all('a', class_=lambda x: x and 'ArticleWrapper' in x)
print(f"\nArticleWrapper 클래스 a 태그 개수: {len(article_wrappers)}")

# div 검색
divs = soup.find_all('div', class_=lambda x: x and 'Article' in x)
print(f"Article 포함 div 개수: {len(divs)}")

# 모든 a 태그 개수
all_a = soup.find_all('a')
print(f"전체 a 태그 개수: {len(all_a)}")

# script 태그 확인 (React 등)
scripts = soup.find_all('script')
print(f"\nscript 태그 개수: {len(scripts)}")

# id="root" 또는 id="app" 확인 (React 앱 시그니처)
root = soup.find('div', id='root')
app = soup.find('div', id='app')
print(f"div#root 존재: {root is not None}")
print(f"div#app 존재: {app is not None}")

# 저장
with open('data/coinness_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print(f"\n✅ 전체 HTML을 data/coinness_debug.html에 저장했습니다.")
print("   이 파일을 열어서 구조를 확인해보세요!")

