// Experiment: live market ticker (flash grid). Self-mounting and no-op when
// the EXPERIMENT_TICKER flag is off (the /api/ticker route 404s).
(function () {
  const REFRESH_MS = 30000;
  const prev = {};
  let bar = null;

  function fmt(v) {
    return v >= 1000
      ? v.toLocaleString('en-US', { maximumFractionDigits: 0 })
      : v.toFixed(v < 10 ? 3 : 2);
  }

  function pillHtml(it) {
    const cls = it.changePct >= 0 ? 'up' : 'down';
    const had = prev[it.id] !== undefined;
    const flash = had && it.price !== prev[it.id] ? (it.price > prev[it.id] ? 'flash-up' : 'flash-down') : '';
    return (
      `<div class="exp-pill ${flash}">` +
      `<div class="exp-pill-top"><span class="exp-zh">${it.zh}</span><span class="exp-sym">${it.sym}</span></div>` +
      `<div class="exp-px">${fmt(it.price)}</div>` +
      `<div class="exp-chg ${cls}">${it.changePct >= 0 ? '▲' : '▼'}${Math.abs(it.changePct).toFixed(2)}%</div>` +
      `</div>`
    );
  }

  async function load() {
    let data;
    try {
      const res = await fetch('/api/ticker');
      if (!res.ok) return false;
      data = await res.json();
    } catch (e) {
      return false;
    }
    if (!data.items || !data.items.length) return true;

    if (!bar) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'experiments/ticker/ticker.css';
      document.head.appendChild(link);
      bar = document.createElement('div');
      bar.className = 'exp-ticker';
      const header = document.querySelector('header.topbar');
      if (header) header.insertAdjacentElement('afterend', bar);
      else document.body.prepend(bar);
    }

    bar.classList.toggle('demo', !!data.demo);
    bar.innerHTML =
      `<span class="exp-ticker-tag">${data.demo ? '示例 DEMO' : '实时 LIVE'}</span>` +
      data.items.map(pillHtml).join('');
    data.items.forEach((it) => (prev[it.id] = it.price));
    return true;
  }

  load().then((ok) => {
    if (ok !== false) setInterval(load, REFRESH_MS);
  });
})();
