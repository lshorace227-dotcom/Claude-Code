// Experiment: live market quotes from free / no-key sources.
// CoinGecko for crypto, Stooq light CSV for indices/FX/commodities.
// Cached for 30s; falls back to bundled sample quotes (random-walked) when
// live sources are unreachable.
const fs = require('fs');
const path = require('path');
const { TTLCache } = require('../../cache');

const cache = new TTLCache();
const TTL = Number(process.env.TICKER_TTL_MS ?? 30000);

const INSTRUMENTS = [
  { id: 'spx', sym: 'S&P 500', zh: '标普500', group: 'idx', source: 'stooq', code: '^spx' },
  { id: 'ndq', sym: 'Nasdaq', zh: '纳斯达克', group: 'idx', source: 'stooq', code: '^ndq' },
  { id: 'dji', sym: 'Dow', zh: '道指', group: 'idx', source: 'stooq', code: '^dji' },
  { id: 'hsi', sym: 'Hang Seng', zh: '恒生', group: 'idx', source: 'stooq', code: '^hsi' },
  { id: 'nkx', sym: 'Nikkei 225', zh: '日经225', group: 'idx', source: 'stooq', code: '^nkx' },
  { id: 'ssec', sym: 'SSE', zh: '上证指数', group: 'idx', source: 'stooq', code: '^shc' },
  { id: 'btc', sym: 'BTC', zh: '比特币', group: 'crypto', source: 'coingecko', code: 'bitcoin' },
  { id: 'eth', sym: 'ETH', zh: '以太坊', group: 'crypto', source: 'coingecko', code: 'ethereum' },
  { id: 'usdcny', sym: 'USD/CNY', zh: '美元/人民币', group: 'fx', source: 'stooq', code: 'usdcny' },
  { id: 'usdjpy', sym: 'USD/JPY', zh: '美元/日元', group: 'fx', source: 'stooq', code: 'usdjpy' },
  { id: 'gold', sym: 'Gold', zh: '黄金', group: 'cmd', source: 'stooq', code: 'xauusd' },
  { id: 'wti', sym: 'WTI Oil', zh: '原油', group: 'cmd', source: 'stooq', code: 'cl.f' },
];

async function fetchWithTimeout(url, asText) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const res = await fetch(url, { signal: ctrl.signal, headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return asText ? res.text() : res.json();
  } finally {
    clearTimeout(timer);
  }
}

async function fetchCoinGecko(items) {
  const ids = items.map((i) => i.code).join(',');
  const data = await fetchWithTimeout(
    `https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true`
  );
  const out = {};
  items.forEach((i) => {
    const q = data[i.code];
    if (q && typeof q.usd === 'number') out[i.id] = { price: q.usd, changePct: q.usd_24h_change || 0 };
  });
  return out;
}

async function fetchStooq(items) {
  const syms = items.map((i) => i.code).join('+');
  const csv = await fetchWithTimeout(
    `https://stooq.com/q/l/?s=${encodeURIComponent(syms)}&f=sd2t2ohlc&h&e=csv`,
    true
  );
  // CSV header: Symbol,Date,Time,Open,High,Low,Close
  const bySym = {};
  csv.trim().split('\n').slice(1).forEach((line) => {
    const [symbol, , , open, , , close] = line.split(',');
    if (symbol) bySym[symbol.toLowerCase()] = { open: parseFloat(open), close: parseFloat(close) };
  });
  const out = {};
  items.forEach((i) => {
    const q = bySym[i.code.toLowerCase()];
    if (q && !isNaN(q.close)) {
      const changePct = q.open ? ((q.close - q.open) / q.open) * 100 : 0;
      out[i.id] = { price: q.close, changePct };
    }
  });
  return out;
}

let sampleState = null;
function loadSample() {
  if (!sampleState) {
    sampleState = JSON.parse(fs.readFileSync(path.join(__dirname, 'sample-quotes.json'), 'utf8'));
  }
  // small random walk so the demo still animates between refreshes
  sampleState.forEach((s) => {
    s.price *= 1 + (Math.random() - 0.5) * 0.004;
  });
  return sampleState.map((s) => ({ ...s }));
}

async function getQuotes() {
  const cached = cache.get('q');
  if (cached) return cached;

  const cg = INSTRUMENTS.filter((i) => i.source === 'coingecko');
  const sq = INSTRUMENTS.filter((i) => i.source === 'stooq');
  const results = await Promise.allSettled([fetchCoinGecko(cg), fetchStooq(sq)]);

  const merged = {};
  results.forEach((r) => {
    if (r.status === 'fulfilled') Object.assign(merged, r.value);
  });

  let demo = false;
  let items;
  if (Object.keys(merged).length < INSTRUMENTS.length / 2) {
    items = loadSample();
    demo = true;
  } else {
    items = INSTRUMENTS.map((i) => ({
      id: i.id,
      sym: i.sym,
      zh: i.zh,
      group: i.group,
      price: merged[i.id] ? merged[i.id].price : null,
      changePct: merged[i.id] ? merged[i.id].changePct : 0,
    })).filter((i) => i.price != null);
  }

  const payload = { updatedAt: new Date().toISOString(), demo, items };
  cache.set('q', payload, TTL);
  return payload;
}

module.exports = { getQuotes, INSTRUMENTS };
