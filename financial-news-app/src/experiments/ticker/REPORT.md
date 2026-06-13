# Implementation Report — Live Market Ticker experiment

**Spec:** `SPEC.md` (same folder) · **Flag:** `EXPERIMENT_TICKER` (off by default)
**Result:** ✅ Implemented in full. All 8 success criteria verified. No deviations from scope.

## What was built

A flag-gated, fully isolated live market ticker (treatment **B — flash grid**) showing
12 instruments (US + Asia indices, BTC/ETH, USD-CNY/USD-JPY, Gold/WTI), refreshing every
30s, using free/no-key data (CoinGecko + Stooq) with a random-walked sample fallback.

New, self-contained code:
- `src/experiments/ticker/quotes.js` — fetch + normalize + 30s cache + sample fallback
- `src/experiments/ticker/route.js` — `mountTicker(app)`, registers `/api/ticker` only when flag on
- `src/experiments/ticker/sample-quotes.json` — offline fallback
- `public/experiments/ticker/ticker.js` / `ticker.css` — self-mounting flash-grid UI

Core-app touch points (the only entanglement, both removable in one edit):
- `server.js`: 1 require/mount line (+ a 2-line deletion comment)
- `public/index.html`: 1 `<script>` line (+ 1 comment)

## Verification results

| # | Criterion | Method | Result |
|---|-----------|--------|--------|
| 1 | Flag off → `/api/ticker` 404, core app unchanged | unit (no route registered) + HTTP on :3100 | ✅ 404; `/` 200; `/api/news` 200 |
| 2 | Flag on → `/api/ticker` 200 with documented shape | unit + HTTP on :3101 | ✅ 200; `{updatedAt, demo, items[12]}` |
| 3 | Live failure → `demo:true`, 12 items | `getQuotes()` in sandbox | ✅ `demo=true`, 12 items |
| 4 | Demo animates (random walk) | TTL=1ms + forced expiry, compare prices | ✅ prices change after expiry |
| 5 | Caching: same `updatedAt` within TTL | two calls within window | ✅ identical `updatedAt` |
| 6 | Frontend assets served + valid | `node --check` + HTTP for js/css | ✅ ticker.js 200 (2040b), ticker.css 200 (1657b), syntax OK |
| 7 | Isolation: 2 touch points only, no other core change | grep + `git diff --stat` | ✅ server.js +5, index.html +2; all else under `*/experiments/ticker/` |
| 8 | No new dependencies | inspect `package.json` | ✅ still `express`, `rss-parser` only |

Module test suite: **8/8 passed** (`/tmp/verify_ticker.js`, not committed).

## Differences from the spec

- **None in scope or behavior.** Minor notes:
  - The verification for C4/C5 surfaced that `TTLCache` treats `ttlMs = 0` as *never
    expire* (not "no cache"); the test therefore used `TICKER_TTL_MS=1` to force expiry.
    This is existing cache behavior, not a code change.
  - As the spec's known-limitations predicted: live data (CoinGecko/Stooq) could not be
    exercised here because the sandbox egress allowlist blocks those hosts, so the
    **demo fallback** path was verified instead. On a normal host, crypto (CoinGecko) is
    reliable and indices/FX/commodities (Stooq) are best-effort.
  - Browser rendering was verified via served assets + JS syntax + DOM-construction review
    rather than a screenshot (no headless browser available in-sandbox).

## How to run / remove

Run with the ticker on:
```bash
EXPERIMENT_TICKER=1 npm start   # → http://localhost:3000
```
Remove the experiment (zero residue): delete `src/experiments/ticker/` and
`public/experiments/ticker/`, then drop the one `mountTicker` line in `server.js` and the
one `<script>` line in `index.html`.
