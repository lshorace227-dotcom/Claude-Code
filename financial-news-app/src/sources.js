// Free financial-news RSS feeds (no API key required).
//   category: default bucket for items from this feed
//   weight:   source authority 1-5, used in the ranking score
const RSS_FEEDS = [
  { url: 'https://www.cnbc.com/id/100003114/device/rss/rss.html', source: 'CNBC', category: 'macro', weight: 4 },
  { url: 'https://www.cnbc.com/id/20910258/device/rss/rss.html', source: 'CNBC Markets', category: 'stocks', weight: 4 },
  { url: 'https://feeds.content.dowjones.io/public/rss/mw_topstories', source: 'MarketWatch', category: 'stocks', weight: 4 },
  { url: 'https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines', source: 'MarketWatch', category: 'stocks', weight: 3 },
  { url: 'https://finance.yahoo.com/news/rssindex', source: 'Yahoo Finance', category: 'macro', weight: 3 },
  { url: 'https://www.investing.com/rss/news_25.rss', source: 'Investing.com', category: 'stocks', weight: 3 },
  { url: 'https://www.investing.com/rss/news_1.rss', source: 'Investing.com FX', category: 'forex', weight: 3 },
  { url: 'https://www.investing.com/rss/news_11.rss', source: 'Investing.com Commodities', category: 'commodities', weight: 3 },
  { url: 'https://www.investing.com/rss/news_301.rss', source: 'Investing.com Crypto', category: 'crypto', weight: 3 },
  { url: 'https://www.coindesk.com/arc/outboundfeeds/rss/', source: 'CoinDesk', category: 'crypto', weight: 4 },
  { url: 'https://www.ft.com/rss/home', source: 'Financial Times', category: 'macro', weight: 5 },
  { url: 'https://seekingalpha.com/market_news.xml', source: 'Seeking Alpha', category: 'stocks', weight: 3 },
  { url: 'https://www.federalreserve.gov/feeds/press_all.xml', source: 'Federal Reserve', category: 'macro', weight: 5 },
];

// UI categories (bilingual labels).
const CATEGORIES = [
  { key: 'all', en: 'All', zh: '全部' },
  { key: 'stocks', en: 'Stocks', zh: '股票' },
  { key: 'forex', en: 'Forex', zh: '外汇' },
  { key: 'crypto', en: 'Crypto', zh: '加密货币' },
  { key: 'commodities', en: 'Commodities', zh: '大宗商品' },
  { key: 'macro', en: 'Macro', zh: '宏观经济' },
];

module.exports = { RSS_FEEDS, CATEGORIES };
