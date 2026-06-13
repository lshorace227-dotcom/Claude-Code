// Frontend: loads categories, top picks and latest news; renders bilingual
// cards; auto-refreshes on an interval (free-tier friendly polling).
const state = {
  category: 'all',
  q: '',
  mode: 'both', // both | zh | en
  lastUpdated: null,
};

const REFRESH_MS = 60000;

const el = (sel) => document.querySelector(sel);

function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}秒前`;
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return `${Math.floor(diff / 86400)}天前`;
}

function escapeHtml(s) {
  return (s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function cardHtml(item, isTop) {
  const cat = `<span class="cat-badge">${escapeHtml(item.category)}</span>`;
  const breaking = item.breaking ? '<span class="breaking-badge">突发 BREAKING</span>' : '';
  const showZh = state.mode !== 'en';
  const showEn = state.mode !== 'zh';

  const titleZh = showZh ? `<p class="title-zh">${escapeHtml(item.title_zh)}</p>` : '';
  const titleEn = showEn ? `<p class="title-en">${escapeHtml(item.title_en)}</p>` : '';
  const sumZh = showZh && item.summary_zh ? `<p class="summary-zh">${escapeHtml(item.summary_zh)}</p>` : '';
  const sumEn = showEn && item.summary_en ? `<p class="summary-en">${escapeHtml(item.summary_en)}</p>` : '';

  return `
    <a class="card${isTop ? ' top' : ''}" href="${escapeHtml(item.url)}" target="_blank" rel="noopener">
      <div class="card-meta">
        ${breaking}${cat}
        <span>${escapeHtml(item.source)}</span>
        <span>· ${timeAgo(item.publishedAt)}</span>
      </div>
      ${titleZh}${titleEn}${sumZh}${sumEn}
    </a>`;
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}

async function loadTabs() {
  try {
    const cats = await fetchJson('/api/categories');
    el('#tabs').innerHTML = cats
      .map(
        (c) =>
          `<button data-cat="${c.key}" class="${c.key === state.category ? 'active' : ''}">${c.zh} <span style="opacity:.6">${c.en}</span></button>`
      )
      .join('');
  } catch (e) {
    console.warn('tabs failed', e);
  }
}

async function refresh() {
  try {
    const params = new URLSearchParams({ category: state.category, q: state.q });
    const [top, news] = await Promise.all([
      fetchJson('/api/top?limit=6'),
      fetchJson('/api/news?' + params.toString()),
    ]);

    el('#demo-banner').classList.toggle('hidden', !news.demo);
    el('#top-grid').innerHTML = top.items.map((i) => cardHtml(i, true)).join('');

    const grid = el('#news-grid');
    grid.innerHTML = news.items.map((i) => cardHtml(i, false)).join('');
    el('#empty').classList.toggle('hidden', news.items.length > 0);

    state.lastUpdated = Date.now();
    updateClock();
  } catch (e) {
    console.error('refresh failed', e);
    el('#live-text').textContent = '连接中断 OFFLINE';
  }
}

function updateClock() {
  if (!state.lastUpdated) return;
  const secs = Math.floor((Date.now() - state.lastUpdated) / 1000);
  el('#updated').textContent = `更新于 ${secs}s 前`;
  el('#live-text').textContent = '实时 LIVE';
}

// --- events ---
el('#tabs').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-cat]');
  if (!btn) return;
  state.category = btn.dataset.cat;
  document.querySelectorAll('#tabs button').forEach((b) => b.classList.toggle('active', b === btn));
  refresh();
});

el('#mode-toggle').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-mode]');
  if (!btn) return;
  state.mode = btn.dataset.mode;
  document.querySelectorAll('#mode-toggle button').forEach((b) => b.classList.toggle('active', b === btn));
  refresh();
});

let searchTimer;
el('#search').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    state.q = e.target.value.trim();
    refresh();
  }, 400);
});

// --- init ---
loadTabs();
refresh();
setInterval(refresh, REFRESH_MS);
setInterval(updateClock, 1000);
