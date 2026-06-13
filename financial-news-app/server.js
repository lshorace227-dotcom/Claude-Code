const path = require('path');
const express = require('express');
const { getNews } = require('./src/aggregator');
const { CATEGORIES } = require('./src/sources');
const { loadTranslationCache, flushTranslationCache } = require('./src/translate');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', (req, res) => res.json({ ok: true, time: new Date().toISOString() }));

app.get('/api/categories', (req, res) => res.json(CATEGORIES));

app.get('/api/news', async (req, res) => {
  try {
    const { category = 'all', q = '', limit } = req.query;
    const data = await getNews({ category, q, limit: limit ? parseInt(limit, 10) : 60, top: false });
    res.json(data);
  } catch (err) {
    console.error('[/api/news]', err);
    res.status(500).json({ error: 'Failed to load news', detail: String(err.message || err) });
  }
});

app.get('/api/top', async (req, res) => {
  try {
    const { limit } = req.query;
    const data = await getNews({ category: 'all', q: '', limit: limit ? parseInt(limit, 10) : 6, top: true });
    res.json(data);
  } catch (err) {
    console.error('[/api/top]', err);
    res.status(500).json({ error: 'Failed to load top news', detail: String(err.message || err) });
  }
});

// --- Experiment: live market ticker (flag-gated, removable) ---
// Delete this line + the src/experiments/ticker and public/experiments/ticker
// folders to remove the experiment entirely.
require('./src/experiments/ticker/route').mountTicker(app);

loadTranslationCache();
const flushTimer = setInterval(flushTranslationCache, 10000);
if (flushTimer.unref) flushTimer.unref();

app.listen(PORT, () => {
  console.log(`Financial news app running on http://localhost:${PORT}`);
});
