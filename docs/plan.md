# Skill Community Bot 설계 문서

## 1. 목표

개발자들이 사용하는 여러 커뮤니티에서 `skill` 관련 글만 수집해서,
필터링 후 지정한 채널(예: Discord, Telegram, 이메일 등)로 전달하는 봇을 만든다.

핵심 목적:
- 여러 커뮤니티를 직접 돌아다니지 않아도 됨
- `skill`, `skills`, `agent skill`, `prompt skill`, `developer skill`, `AI skill` 등과 관련된 글만 모아서 볼 수 있음
- 관심 있는 정보만 빠르게 수집할 수 있음

---

## 2. 이 봇이 하는 일

이 봇의 역할은 크게 4단계다.

1. 여러 개발자 커뮤니티에서 새 글 수집
2. 글 제목/본문/태그를 기준으로 skill 관련성 판별
3. 관련도 높은 글만 선별
4. 결과를 지정한 채널로 전달

즉, 단순 크롤러가 아니라 **수집 + 필터링 + 전달** 역할을 한다.

---

## 3. 수집 대상 후보 커뮤니티

우선순위 기준으로 정리하면:

### 1순위
- GitHub Trending / GitHub Discussions
- DEV Community (dev.to)
- Hacker News
- Reddit (관련 서브레딧)

### 2순위
- Product Hunt
- Lobsters
- Indie Hackers
- 특정 Discord/Telegram 공개 채널

### 3순위
- Medium 태그 검색
- Substack 기술 뉴스레터
- 공식 블로그(RSS 제공 시)

초기 MVP는 **RSS 또는 공개 HTML/공개 API가 있는 곳만 우선** 붙이는 게 좋다.

---

## 4. 핵심 설계 방향

### 방향 1. 처음부터 모든 커뮤니티를 붙이지 않는다
가장 먼저 2~3개 소스만 붙인다.

추천 시작 조합:
- DEV Community
- Hacker News
- GitHub Trending 또는 GitHub Discussions

### 방향 2. 키워드 필터만으로 끝내지 않는다
처음엔 키워드 필터로 시작할 수 있지만,
점점 아래 같은 방식이 필요해진다.

- 제목 키워드 포함 여부
- 본문/요약 포함 여부
- 태그 매칭
- 중복 제거
- AI 기반 relevance scoring

### 방향 3. 전달 채널은 1개부터 시작
초기 MVP는 Discord 또는 Telegram 중 하나만 붙이는 것이 좋다.

---

## 5. 추천 시스템 구조

```text
[Source Collector]
  -> GitHub / DEV / HN / Reddit 수집

[Normalizer]
  -> 제목, 링크, 작성일, 본문 요약, 출처 형태 통일

[Filter]
  -> skill 관련 키워드/태그/AI relevance 판별

[Deduplicator]
  -> 같은 링크/유사 글 제거

[Notifier]
  -> Discord / Telegram / Email 전송
```

---

## 6. MVP 기준 기능

### 필수
- 2~3개 커뮤니티 수집
- skill 관련 글 필터링
- 중복 제거
- Discord 또는 Telegram 알림
- 최근 수집 로그 저장

### 있으면 좋은 것
- 수집 주기 설정
- 필터 키워드 편집
- 관심도 점수
- 요약 메시지 생성

### 나중에 추가
- 관리자 페이지
- 사용자별 관심 키워드
- 다중 채널 전송
- 개인화 추천

---

## 7. skill 관련 판별 기준

처음엔 아래 키워드 세트로 출발 가능:

### 기본 키워드
- skill
- skills
- agent skill
- AI skill
- developer skill
- prompt skill
- marketplace skill
- reusable skill
- skill library
- skill system

### 함께 보면 좋은 연관 키워드
- agent
- workflow
- automation
- prompt
- template
- library
- tooling
- reusable

### 필터 전략
1. 제목 우선 매칭
2. 태그 매칭
3. 본문 요약 매칭
4. AI relevance 점수로 2차 필터링

---

## 8. 추천 구현 방식

### 방법 A. Python/Node 백엔드 + 스케줄러
추천도 높음.

이유:
- 여러 소스 수집 유연함
- GitHub repo로 관리 쉬움
- 나중에 확장 쉬움

구성 예시:
- 수집 스크립트
- 필터 모듈
- SQLite/Postgres 저장
- Discord webhook 또는 Telegram bot 알림
- cron 또는 GitHub Actions 실행

### 방법 B. n8n 기반
가능하지만,
커뮤니티 소스가 많아지고 필터 로직이 복잡해지면 코드 방식이 더 유리할 수 있다.

### 내 추천
처음엔 **코드 방식(Node 또는 Python)** 이 더 적합하다.

---

## 9. 저장 구조 예시

```text
sources
- id
- name
- type
- fetch_method

posts
- id
- source_name
- title
- url
- summary
- tags
- published_at
- matched_keywords
- relevance_score
- sent
```

---

## 10. 알림 메시지 예시

```text
[DEV Community]
제목: Building a reusable AI skill library
관련 키워드: skill, reusable, library
링크: https://...
```

또는

```text
[Hacker News] skill 관련 글 감지
- 제목: ...
- 이유: title match + summary match
- 링크: ...
```

---

## 11. 추천 개발 순서

### 1단계
- 소스 2개 선택
- 수집 성공

### 2단계
- 키워드 필터링 구현
- 중복 제거 구현

### 3단계
- Discord 또는 Telegram 알림 연결

### 4단계
- 로그 저장
- relevance scoring 추가

### 5단계
- 소스 확장
- 관리자/설정 기능 고민

---

## 12. 구현 전에 꼭 정해야 할 질문

1. 어떤 커뮤니티를 1차 대상으로 할지?
2. 알림은 Discord로 받을지, Telegram으로 받을지?
3. `skill`의 범위를 어디까지 볼지?
   - AI agent skill
   - 개발자 스킬/커리어 글
   - 프롬프트/워크플로 템플릿
4. 단순 키워드 필터로 시작할지, AI relevance를 바로 넣을지?
5. 개인용 봇인지, 나중에 여러 사람이 함께 쓰는 서비스인지?

---

## 13. 현재 기준 추천 결론

이 프로젝트는 처음부터 복잡하게 만들기보다,
다음과 같이 시작하는 것이 가장 좋다.

### 추천 MVP
- 소스: DEV Community + Hacker News + GitHub Trending
- 필터: 키워드 + 간단 점수화
- 전달: Discord
- 저장: SQLite 또는 Postgres

즉,
**먼저 3개 커뮤니티에서 skill 관련 글만 골라 Discord로 보내는 봇**
이 1차 버전으로 가장 적절하다.
