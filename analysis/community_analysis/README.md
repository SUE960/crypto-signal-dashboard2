# Community Analysis - 데이터 전처리 모듈

커뮤니티 감성 분석을 위한 데이터 전처리 스크립트 모음

## 📁 파일 구조

```
community_analysis/
├── data/                           # 전처리된 데이터 저장 폴더
│   ├── community_ts_1h.csv         # 1시간 단위 시계열
│   ├── community_ts_4h.csv         # 4시간 단위 시계열
│   ├── community_ts_1d.csv         # 1일 단위 시계열
│   ├── community_spike_events.csv  # 스파이크 이벤트
│   ├── community_top_posts_*.csv   # 인기 게시글 (기간별)
│   └── community_keywords_*.csv    # 키워드 통계 (기간별)
├── preprocess_timeseries.py        # 시계열 데이터 전처리
├── preprocess_spike.py             # 스파이크 탐지
├── preprocess_top_posts.py         # 인기 게시글 추출
├── preprocess_top_posts_periodic.py # 기간별 인기 게시글
├── preprocess_keywords.py          # 키워드 추출 (NLTK)
└── preprocess_keywords_periodic.py # 기간별 키워드 통계
```

## 🔧 전처리 스크립트

### 1. preprocess_timeseries.py

시간 단위별 감성 통계 집계

**출력**: `community_ts_{freq}.csv`
| 컬럼 | 설명 |
|------|------|
| post_date | 집계 시간 |
| avg_sentiment | 평균 감성 점수 |
| variance | 감성 분산 |
| total_posts | 총 게시글 수 |
| pos/neg/neu | 긍정/부정/중립 비율 |

### 2. preprocess_spike.py

Z-score 기반 감성 급변(스파이크) 탐지

**출력**: `community_spike_events.csv`
| 컬럼 | 설명 |
|------|------|
| timestamp | 스파이크 발생 시간 |
| zscore | Z-score 값 |
| threshold | 적용된 임계값 |
| diff | 이전 대비 변화량 |

**알고리즘**:

```python
zscore = (current_sentiment - rolling_mean) / rolling_std
spike = zscore >= threshold  # 기본 threshold=2.0
```

### 3. preprocess_top_posts.py

참여도 점수 기반 인기 게시글 추출

**점수 계산**:

```python
engagement_score = (comments * 3) + (shares * 2) + (likes * 1)
```

**출력**: `community_top_posts.csv`

### 4. preprocess_top_posts_periodic.py

기간별(일/주/월) 인기 게시글 추출

**출력**:

- `community_top_posts_daily.csv`
- `community_top_posts_weekly.csv`
- `community_top_posts_monthly.csv`

### 5. preprocess_keywords.py

NLTK 기반 키워드 추출 및 감성 분석

**NLP 처리**:

```python
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# 불용어 제거 + 명사/동사만 추출
stop_words = set(stopwords.words('english'))
tokens = word_tokenize(text)
tagged = pos_tag(tokens)
keywords = [word for word, tag in tagged
            if tag.startswith(('NN', 'VB')) and word not in stop_words]
```

**출력**: `community_keywords_freq.csv`
| 컬럼 | 설명 |
|------|------|
| word | 키워드 |
| total_count | 총 출현 횟수 |
| positive | 긍정 게시글 출현 수 |
| negative | 부정 게시글 출현 수 |
| neutral | 중립 게시글 출현 수 |

### 6. preprocess_keywords_periodic.py

기간별 키워드 통계

**출력**:

- `community_keywords_daily.csv`
- `community_keywords_weekly.csv`
- `community_keywords_monthly.csv`

## 🚀 실행 방법

```bash
cd analysis/community_analysis

# 1. 시계열 데이터 생성
python preprocess_timeseries.py

# 2. 스파이크 탐지
python preprocess_spike.py

# 3. 인기 게시글 추출
python preprocess_top_posts.py
python preprocess_top_posts_periodic.py

# 4. 키워드 추출 (NLTK 필요)
python preprocess_keywords.py
python preprocess_keywords_periodic.py
```

## 📦 의존성

```bash
pip install pandas numpy nltk
```

NLTK 데이터 다운로드:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
```

## 🔄 데이터 흐름

```
원본 데이터 (CSV/DB)
        ↓
┌───────────────────────────────────┐
│     전처리 스크립트 (Python)       │
│  - 시계열 집계                     │
│  - 스파이크 탐지                   │
│  - 키워드 추출 (NLTK)              │
│  - 인기 게시글 추출                │
└───────────────────────────────────┘
        ↓
    data/ 폴더 (CSV)
        ↓
┌───────────────────────────────────┐
│     Next.js API Routes            │
│  - /api/community/sentiment       │
│  - /api/community/spikes          │
│  - /api/community/wordcloud       │
│  - /api/community/top-posts       │
└───────────────────────────────────┘
        ↓
    Community Dashboard (React)
```

## 📊 Dashboard 연동

전처리된 데이터는 Next.js API를 통해 프론트엔드에서 사용:

| API 엔드포인트             | 사용 데이터                  | 컴포넌트        |
| -------------------------- | ---------------------------- | --------------- |
| `/api/community/sentiment` | `community_ts_*.csv`         | SentimentTrend  |
| `/api/community/spikes`    | `community_spike_events.csv` | SpikeTimeline   |
| `/api/community/top-posts` | `community_top_posts_*.csv`  | TopPosts        |
| `/api/community/wordcloud` | `community_keywords_*.csv`   | KeywordAnalysis |
