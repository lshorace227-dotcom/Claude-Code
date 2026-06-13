# Spec — Experiment: Live Market Ticker

**Status:** experimental · disposable (may be deleted within ~1 month)
**Owner flag:** `EXPERIMENT_TICKER` (off by default)
**Decided via interview:** treatment **B (flash grid)**, instruments **Global + Asia mix**, refresh **30s**, **no new dependencies / no API keys**, isolated module + flag.

## 1. Goal

Add a live market ticker strip to the financial news app to test whether at-a-glance
prices increase engagement — built so it can be removed in a single commit with **zero
residue** in the core app.

## 2. Scope

- A horizontal **flash-grid** of price pills below the site header.
- 12 instruments across 4 groups:
  - **Indices:** S&P 500 (标普500), Nasdaq (纳斯达克), Dow (道指), Hang Seng (恒生), Nikkei 225 (日经225), SSE (上证指数)
  - **Crypto:** BTC (比特币), ETH (以太坊)
  - **FX:** USD/CNY (美元/人民币), USD/JPY (美元/日元)
  - **Commodities:** Gold (黄金), WTI Oil (原油)
- Each pill: bilingual name, price, day change % (green ▲ / red ▼); the pill **flashes**
  green/red when its price moves.
- Refresh every **30s** (frontend poll; backend caches for 30s).

### Non-goals
- No historical charts, no order book, no per-instrument detail pages.
- No new npm dependencies; no API keys.
- No changes to the news feed, translation, or ranking logic.
- Ticker is **not** sticky (avoids reworking the existing sticky header/controls offsets).

## 3. Data sources (free, no key)

| Group | Source | Endpoint | Notes |
|---|---|---|---|
| Crypto | **CoinGecko** | `/api/v3/simple/price?ids=…&vs_currencies=usd&include_24hr_change=true` | Reliable, keyless |
| Indices / FX / Commodities | **Stooq** light CSV | `https://stooq.com/q/l/?s=<sym>+<sym>&f=sd2t2ohlc&e=csv` | Keyless, best-effort; day change = (close-open)/open |

If live sources fail (e.g. the sandbox egress allowlist blocks them), the API returns
**bundled sample quotes** with `demo:true`, jittered by a small random walk so the UI
still animates.

## 4. Architecture & file layout (all new code is isolated)

```
financial-news-app/
├─ src/experiments/ticker/
│  ├─ quotes.js          # fetch (CoinGecko + Stooq) → normalize → cache → sample fallback
│  ├─ route.js           # mountTicker(app): registers GET /api/ticker ONLY when flag on
│  └─ sample-quotes.json # offline fallback
├─ public/experiments/ticker/
│  ├─ ticker.js          # builds the bar, polls /api/ticker, flashes on change
│  └─ ticker.css         # .exp-* scoped styles
```

Two one-line touch points in core files (the only entanglement):
- `server.js`: `require('./src/experiments/ticker/route').mountTicker(app);`
- `public/index.html`: `<script defer src="experiments/ticker/ticker.js"></script>`

## 5. Feature flag behavior

- **Off (default):** `mountTicker` registers no route → `GET /api/ticker` 404s →
  `ticker.js` fetches once, sees non-200, and no-ops (no DOM inserted). App is byte-for-byte
  unchanged in behavior.
- **On (`EXPERIMENT_TICKER=1`):** route active; ticker renders and polls.

## 6. API contract

`GET /api/ticker` →
```json
{
  "updatedAt": "ISO-8601",
  "demo": false,
  "items": [
    { "id": "spx", "sym": "S&P 500", "zh": "标普500", "group": "idx",
      "price": 5123.4, "changePct": 0.42 }
  ]
}
```

## 7. Disposability — removal steps

1. Delete `src/experiments/ticker/` and `public/experiments/ticker/`.
2. Remove the one `require(...).mountTicker(app)` line in `server.js`.
3. Remove the one `<script ... ticker.js>` line in `index.html`.

No shared modules are modified (the ticker only *imports* the existing `TTLCache`; it
adds nothing to it).

## 8. Success criteria (verified in the report)

1. **Flag off:** `/api/ticker` → 404; served `index.html` unchanged; no ticker code runs.
2. **Flag on:** `/api/ticker` → 200 JSON with the documented shape.
3. **Fallback:** when live sources are blocked, response has `demo:true` and all 12 items.
4. **Demo animation:** consecutive *uncached* responses show changed prices (random walk).
5. **Caching:** two calls within 30s share the same `updatedAt` (served from cache).
6. **Frontend:** `ticker.js` / `ticker.css` are served (200) and JS is syntactically valid;
   the bar inserts after `header.topbar` and renders flash-grid pills.
7. **Isolation:** experiment code is confined to the two folders + exactly two one-line
   touch points; no other core file changed.
8. **No new deps:** `package.json` dependencies unchanged.

## 9. Risks / known limitations

- Stooq/Yahoo keyless quotes are **best-effort** (no SLA); crypto via CoinGecko is the only
  fully reliable leg. The sample fallback covers outages.
- Ticker is non-sticky by design (disposability over polish).
- Browser rendering can't be screenshotted in this sandbox; verified via served assets,
  syntax checks, and DOM-construction review rather than a live screenshot.
