# Skill Community Bot

개발자 커뮤니티에서 `skill` 관련 글만 수집해서 Discord로 전달하는 봇

## 기능

- DEV Community, Hacker News, GitHub Trending, Reddit에서 글 수집
- skill 관련 키워드 필터링
- 중복 제거
- Discord 알림 전송

## 설치

```bash
pip install -r requirements.txt
```

## 환경 변수 설정

`.env` 파일 생성:

```
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id

REDDIT_USER_AGENT=SkillCommunityBot/1.0
```

`REDDIT_USER_AGENT`만 있으면 public subreddit JSON endpoint를 읽을 수 있습니다.

## 실행

```bash
python main.py
```

## 프로젝트 구조

```
.
├── main.py              # 메인 실행 파일
├── config.py            # 설정
├── database.py          # SQLite 데이터베이스
├── collectors/          # 커뮤니티 수집기
│   ├── __init__.py
│   ├── base.py
│   ├── dev_community.py
│   ├── hacker_news.py
│   ├── github_trending.py
│   ├── reddit.py
│   └── hada_news.py
├── filters/             # 필터링 로직
│   ├── __init__.py
│   └── keyword_filter.py
├── notifier/            # 알림
│   ├── __init__.py
│   └── discord_bot.py
└── requirements.txt
```
