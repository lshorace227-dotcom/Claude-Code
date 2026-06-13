# 全球金融新闻平台 · Global Financial News

A real-time, bilingual (Chinese–English) global financial news web app. It
aggregates news from **free / freemium** sources, recommends top market-moving
stories, and shows every article in **中英对照** (Chinese + English) side by side.

## Features

- **Real-time updates** — the frontend auto-refreshes every 60s; the backend
  re-fetches sources at most once per minute (cached in between).
- **Comprehensive free sources** — 13 financial RSS feeds out of the box
  (CNBC, MarketWatch, Yahoo Finance, Investing.com, CoinDesk, FT, Seeking Alpha,
  the Federal Reserve, …), plus optional freemium APIs (NewsAPI, GNews, Finnhub,
  Marketaux) when you add keys.
- **Top picks / 重点推荐** — ranks stories by recency, source authority, impact
  keywords, and sentiment; flags **breaking** news.
- **Bilingual display** — every headline and summary is shown in both Chinese
  and English (machine translation via Google's free endpoint, cached to disk).
- **Categories & search** — All / Stocks / Forex / Crypto / Commodities / Macro,
  plus full-text search.
- **Resilient** — caches results, de-duplicates, throttles, and falls back to
  bundled sample data if every live source is unreachable.

## Quick start

```bash
npm install
npm start
# open http://localhost:3000
```

No API keys are required — RSS feeds work on their own. To widen coverage, copy
`.env.example` to `.env` and add any free-tier keys:

```bash
cp .env.example .env
# then fill in NEWSAPI_KEY / GNEWS_KEY / FINNHUB_KEY / MARKETAUX_KEY
```

## Tech stack

- **Backend:** Node.js + Express, `rss-parser`, built-in `fetch`
- **Frontend:** vanilla HTML/CSS/JS (no build step)
- **Translation:** Google free translate endpoint, memoized in
  `data/translations.json`

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/news?category=&q=&limit=` | Latest news (newest first), bilingual |
| `GET /api/top?limit=` | Top recommended / breaking news (ranked) |
| `GET /api/categories` | Category list (bilingual labels) |
| `GET /api/health` | Health check |

## Notes & limits

- **Network:** if you run this in a sandbox with an egress allowlist, add the
  news hosts (and `translate.googleapis.com`) to the allowlist, or the app will
  fall back to sample data.
- **Quotas:** translations are cached on disk so the same text is never
  re-translated; raw feeds are cached for 60s to respect rate limits.
- **Translation quality:** machine-translated text is for reference only.

## Project layout

```
financial-news-app/
├─ server.js              # Express server + routes
├─ src/
│  ├─ aggregator.js       # fetch + normalize + dedupe + categorize + rank
│  ├─ sources.js          # RSS feed list + categories
│  ├─ translate.js        # bilingual translation + caching
│  └─ cache.js            # TTL cache
├─ public/                # frontend (index.html, styles.css, app.js)
└─ data/
   ├─ sample-news.json    # offline fallback
   └─ translations.json   # generated translation cache (gitignored)
```
