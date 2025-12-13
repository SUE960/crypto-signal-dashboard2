# 크립토 시그널 대시보드 배포 가이드

## 🚀 Streamlit Cloud 배포

### 1단계: GitHub 저장소 준비

```bash
# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit: Crypto Signal Dashboard"

# GitHub 저장소 생성 후
git remote add origin https://github.com/YOUR_USERNAME/crypto-signal-dashboard.git
git push -u origin main
```

### 2단계: Streamlit Cloud 배포

1. **Streamlit Cloud 접속**: https://share.streamlit.io/
2. **New app** 클릭
3. **저장소 연결**:
   - Repository: `YOUR_USERNAME/crypto-signal-dashboard`
   - Branch: `main`
   - Main file path: `app_new.py`
4. **고급 설정** (Advanced settings):
   - Python version: `3.11`
   - Requirements file: `requirements_deploy.txt`
5. **Deploy!** 클릭

### 3단계: 데이터 파일 업로드

Streamlit Cloud에서는 로컬 데이터 파일을 직접 사용할 수 없으므로:

**옵션 A: GitHub에 데이터 포함**
```bash
# data 폴더를 Git에 추가
git add data/*.csv
git commit -m "Add data files"
git push
```

**옵션 B: 외부 스토리지 사용** (추천)
- Google Drive, AWS S3, 또는 GitHub Releases에 CSV 업로드
- `app_new.py`에서 URL로 데이터 로드 추가

---

## 🖥️ 로컬 실행

```bash
# 새 앱 실행
streamlit run app_new.py

# 또는 기존 앱
streamlit run app.py
```

---

## 📊 주요 기능

### ✅ 완료된 기능

1. **3가지 데이터 소스 통합**
   - 텔레그램 커뮤니티 활동
   - 코인니스 뉴스 (수집 중)
   - 트위터 인플루언서

2. **종합 점수 시스템**
   - 가중치: 텔레그램 30%, 뉴스 40%, 트위터 30%
   - 실시간 시장 신호 생성

3. **모던 블랙 테마 UI**
   - 사이드바 제거
   - 상단 네비게이션
   - 그라데이션 카드 디자인

4. **스파이크 알람**
   - 실시간 이상 감지
   - 시계열 표시

5. **차익거래 CTA**
   - https://whale-arbitrage-qwodzy8wpnhpgxaxt23rj8.streamlit.app/

---

## 🔧 환경 변수 (필요시)

Streamlit Cloud의 **Settings > Secrets**에 추가:

```toml
# .streamlit/secrets.toml
[data]
processed_data_url = "https://your-storage-url/processed_data.csv"
```

---

## 📁 프로젝트 구조

```
big_data/
├── app_new.py              # 새 메인 대시보드
├── requirements_deploy.txt # 배포용 패키지
├── .streamlit/
│   └── config.toml        # Streamlit 설정
├── data/
│   ├── processed_data.csv
│   ├── telegram_data.csv
│   ├── coinness_data.csv
│   └── twitter_influencer_labeled_rows.csv
├── utils/
│   ├── data_loader.py
│   ├── sentiment_analyzer.py
│   └── composite_score.py
└── analysis/
    ├── correlation_analysis.py
    └── spike_detector.py
```

---

## 🎯 다음 단계

1. **코인니스 수집 완료 대기** (현재 진행 중)
2. **데이터 파일을 GitHub에 푸시**
3. **Streamlit Cloud 배포**
4. **실시간 모니터링 시작**

---

## 🐛 트러블슈팅

### 문제: ModuleNotFoundError
```bash
# 로컬에서 테스트
pip install -r requirements_deploy.txt
streamlit run app_new.py
```

### 문제: 데이터 파일을 찾을 수 없음
- `app_new.py`의 데이터 경로를 상대 경로로 수정
- 또는 Streamlit Secrets에 URL 추가

### 문제: 메모리 초과
- Streamlit Cloud 무료 플랜: 1GB RAM
- 큰 데이터 파일은 샘플링하여 사용

---

**🎉 완료! 이제 실행해보세요:**

```bash
streamlit run app_new.py
```





