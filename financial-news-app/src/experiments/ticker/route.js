// Experiment: ticker route. Registers GET /api/ticker ONLY when the
// EXPERIMENT_TICKER flag is on, so the feature is invisible by default.
const { getQuotes } = require('./quotes');

const FLAG = ['1', 'true', 'on', 'yes'].includes(
  String(process.env.EXPERIMENT_TICKER || '').toLowerCase()
);

function mountTicker(app) {
  if (!FLAG) {
    console.log('[experiment:ticker] disabled (set EXPERIMENT_TICKER=1 to enable)');
    return;
  }
  app.get('/api/ticker', async (req, res) => {
    try {
      res.json(await getQuotes());
    } catch (err) {
      console.error('[/api/ticker]', err);
      res.status(500).json({ error: 'ticker failed', detail: String(err.message || err) });
    }
  });
  console.log('[experiment:ticker] enabled at /api/ticker');
}

module.exports = { mountTicker };
