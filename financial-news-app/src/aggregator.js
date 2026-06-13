// Fetches news from free RSS feeds (+ optional freemium APIs when keys are
// present), normalizes, de-duplicates, categorizes, ranks, and adds bilingual
// text. Raw items are cached briefly to respect rate limits.
const fs = require('fs');
const path = require('path');
const Parser = require('rss-parser');
const { RSS_FEEDS } = require('./sources');
const { TTLCache } = require('./cache');
const { toBilingual } = require('./translate');

const parser = new Parser({
  timeout: 10000,
  headers: { 'User-Agent': 'Mozilla/5.0 (FinNewsBot)' },
});
const cache = new TTLCache();
const RAW_TTL = 60 * 1000; // re-fetch sources at most once per minute

// Impact keywords used to flag market-moving / breaking news.
const IMPACT = /\b(breaking|surge|soar|plunge|crash|tumble|rally|jump|slump|fed|rate hike|rate cut|inflation|recession|earnings|results|war|crisis|default|bankrupt|merger|acquisition|ipo|sanction|tariff|record high|record low)\b/i;
const IMPACT_ZH = /(暴涨|暴跌|大涨|大跌|加息|降息|通胀|衰退|财报|危机|违约|破产|并购|制裁|关税|突发|创新高|创新低)/;

function stripHtml(s) {
  return (s || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
}

function hoursAgo(dateStr) {
  const t = new Date(dateStr).getTime();
  if (isNaN(t)) return 999;
  return (Date.now() - t) / 36e5;
}

function categorize(fallback, text) {
  const t = (text || '').toLowerCase();
  if (/bitcoin|crypto|ethereum|token|blockchain|\bcoin\b/.test(t)) return 'crypto';
  if (/forex|currency|dollar|euro|\byen\b|exchange rate|\bfx\b/.test(t)) return 'forex';
  if (/\boil\b|gold|crude|commodity|copper|natural gas|silver|wheat/.test(t)) return 'commodities';
  if (/stock|share|equit|earnings|nasdaq|\bdow\b|s&p|index/.test(t)) return 'stocks';
  if (/\b(fed|inflation|gdp|economy|rate|central bank|unemployment|treasury)\b/.test(t)) return 'macro';
  return fallback || 'macro';
}

function normalize({ title, summary, url, source, weight, publishedAt, image, sentiment, category }) {
  return {
    titleRaw: stripHtml(title),
    summaryRaw: stripHtml(summary).slice(0, 400),
    url,
    source,
    weight: weight || 3,
    category: category || categorize(null, `${title} ${summary}`),
    publishedAt: publishedAt || new Date().toISOString(),
    image: image || null,
    sentiment: sentiment || 0,
  };
}

function scoreItem(item) {
  const recency = Math.max(0, 48 - hoursAgo(item.publishedAt)) / 48; // 0..1
  const text = `${item.titleRaw} ${item.summaryRaw}`;
  const impact = IMPACT.test(text) || IMPACT_ZH.test(text) ? 1 : 0;
  const sentiment = Math.min(1, Math.abs(item.sentiment || 0));
  return recency * 5 + (item.weight || 3) * 0.6 + impact * 2 + sentiment * 1.5;
}

function isBreaking(item) {
  const text = `${item.titleRaw} ${item.summaryRaw}`;
  return hoursAgo(item.publishedAt) < 1.5 && (IMPACT.test(text) || IMPACT_ZH.test(item.titleRaw));
}

async function fetchRssFeed(feed) {
  try {
    const parsed = await parser.parseURL(feed.url);
    return (parsed.items || []).slice(0, 15).map((it) =>
      normalize({
        title: it.title,
        summary: it.contentSnippet || it.content || it.summary || '',
        url: it.link,
        source: feed.source,
        weight: feed.weight,
        publishedAt: it.isoDate || it.pubDate,
        image: it.enclosure && it.enclosure.url,
        category: categorize(feed.category, `${it.title} ${it.contentSnippet || ''}`),
      })
    );
  } catch (e) {
    console.warn(`[rss] ${feed.source} failed: ${e.message}`);
    return [];
  }
}

async function jget(url, opts) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 9000);
  try {
    const res = await fetch(url, { ...opts, signal: ctrl.signal });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

// Optional freemium providers — only queried when an API key is configured.
async function fetchApiProviders() {
  const out = [];
  const tasks = [];

  if (process.env.NEWSAPI_KEY) {
    tasks.push(
      jget(`https://newsapi.org/v2/top-headlines?category=business&language=en&pageSize=30&apiKey=${process.env.NEWSAPI_KEY}`)
        .then((d) => (d.articles || []).forEach((a) =>
          out.push(normalize({ title: a.title, summary: a.description, url: a.url, source: (a.source && a.source.name) || 'NewsAPI', weight: 4, publishedAt: a.publishedAt, image: a.urlToImage }))))
    );
  }
  if (process.env.GNEWS_KEY) {
    tasks.push(
      jget(`https://gnews.io/api/v4/top-headlines?category=business&lang=en&max=30&token=${process.env.GNEWS_KEY}`)
        .then((d) => (d.articles || []).forEach((a) =>
          out.push(normalize({ title: a.title, summary: a.description, url: a.url, source: (a.source && a.source.name) || 'GNews', weight: 3, publishedAt: a.publishedAt, image: a.image }))))
    );
  }
  if (process.env.FINNHUB_KEY) {
    tasks.push(
      jget(`https://finnhub.io/api/v1/news?category=general&token=${process.env.FINNHUB_KEY}`)
        .then((d) => (Array.isArray(d) ? d : []).slice(0, 30).forEach((a) =>
          out.push(normalize({ title: a.headline, summary: a.summary, url: a.url, source: a.source || 'Finnhub', weight: 4, publishedAt: a.datetime ? new Date(a.datetime * 1000).toISOString() : null, image: a.image }))))
    );
  }
  if (process.env.MARKETAUX_KEY) {
    tasks.push(
      jget(`https://api.marketaux.com/v1/news/all?language=en&filter_entities=true&limit=30&api_token=${process.env.MARKETAUX_KEY}`)
        .then((d) => (d.data || []).forEach((a) => {
          const ents = a.entities || [];
          const sentiment = ents.length ? ents.reduce((s, e) => s + (e.sentiment_score || 0), 0) / ents.length : 0;
          out.push(normalize({ title: a.title, summary: a.description, url: a.url, source: a.source || 'Marketaux', weight: 4, publishedAt: a.published_at, image: a.image_url, sentiment }));
        }))
    );
  }

  if (!tasks.length) return [];
  await Promise.allSettled(tasks);
  return out;
}

// Offline fallback so the UI is never empty when live sources are blocked or
// down. Timestamps are spread across recent hours so it reads as "live".
function loadSample() {
  const file = path.join(__dirname, '..', 'data', 'sample-news.json');
  const items = JSON.parse(fs.readFileSync(file, 'utf8'));
  return items.map((it, i) =>
    normalize({
      ...it,
      title: it.title,
      summary: it.summary,
      publishedAt: new Date(Date.now() - i * 27 * 60 * 1000).toISOString(),
    })
  ).map((it) => ({ ...it, demo: true }));
}

function dedupe(items) {
  const seen = new Set();
  return items.filter((it) => {
    const key = (it.url || it.titleRaw || '').toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function collectRaw() {
  const cached = cache.get('raw');
  if (cached) return cached;

  const results = await Promise.all([...RSS_FEEDS.map(fetchRssFeed), fetchApiProviders()]);
  let items = dedupe(results.flat());
  let demo = false;
  if (items.length === 0) {
    items = loadSample();
    demo = true;
  }
  const payload = { items, demo };
  cache.set('raw', payload, RAW_TTL);
  return payload;
}

// Concurrency-limited async map (keeps translation calls in check).
async function mapLimit(arr, limit, fn) {
  const out = [];
  let i = 0;
  const workers = Array.from({ length: Math.min(limit, arr.length) }, async () => {
    while (i < arr.length) {
      const idx = i++;
      out[idx] = await fn(arr[idx]);
    }
  });
  await Promise.all(workers);
  return out;
}

async function getNews({ category = 'all', q = '', limit = 60, top = false } = {}) {
  const { items, demo } = await collectRaw();

  let list = items;
  if (category && category !== 'all') list = list.filter((it) => it.category === category);
  if (q) {
    const needle = q.toLowerCase();
    list = list.filter((it) => `${it.titleRaw} ${it.summaryRaw}`.toLowerCase().includes(needle));
  }

  list = list.map((it) => ({ ...it, score: scoreItem(it), breaking: isBreaking(it) }));
  list.sort((a, b) => (top ? b.score - a.score : new Date(b.publishedAt) - new Date(a.publishedAt)));
  list = list.slice(0, limit);

  const enriched = await mapLimit(list, 6, async (it) => {
    const [title, summary] = await Promise.all([toBilingual(it.titleRaw), toBilingual(it.summaryRaw)]);
    return {
      id: Buffer.from(`${it.url || it.titleRaw}|${it.publishedAt}`).toString('base64url'),
      title_en: title.en,
      title_zh: title.zh,
      summary_en: summary.en,
      summary_zh: summary.zh,
      source: it.source,
      url: it.url,
      category: it.category,
      publishedAt: it.publishedAt,
      image: it.image,
      breaking: it.breaking,
      demo: !!it.demo,
    };
  });

  return { updatedAt: new Date().toISOString(), demo, count: enriched.length, items: enriched };
}

module.exports = { getNews };
