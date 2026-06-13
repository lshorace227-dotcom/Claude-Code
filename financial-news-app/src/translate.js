// Bilingual translation via Google's free translate endpoint.
// Translations are memoized in memory and persisted to disk so we never
// re-translate the same text (saves quota and keeps the UI fast).
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CACHE_FILE = path.join(__dirname, '..', 'data', 'translations.json');
const memo = new Map(); // key -> translated text
let dirty = false;

function hash(s) {
  return crypto.createHash('md5').update(s).digest('hex');
}

function hasCJK(s) {
  return /[一-鿿㐀-䶿]/.test(s);
}

function loadTranslationCache() {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const obj = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
      for (const [k, v] of Object.entries(obj)) memo.set(k, v);
      console.log(`[translate] loaded ${memo.size} cached translations`);
    }
  } catch (e) {
    console.warn('[translate] cache load failed:', e.message);
  }
}

function flushTranslationCache() {
  if (!dirty) return;
  try {
    fs.mkdirSync(path.dirname(CACHE_FILE), { recursive: true });
    fs.writeFileSync(CACHE_FILE, JSON.stringify(Object.fromEntries(memo)));
    dirty = false;
  } catch (e) {
    console.warn('[translate] cache flush failed:', e.message);
  }
}

async function gtxTranslate(text, target) {
  const url =
    'https://translate.googleapis.com/translate_a/single' +
    `?client=gtx&sl=auto&tl=${target}&dt=t&q=${encodeURIComponent(text)}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 8000);
  try {
    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: { 'User-Agent': 'Mozilla/5.0' },
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    return (data[0] || []).map((seg) => seg[0]).join('');
  } finally {
    clearTimeout(timer);
  }
}

// Translate text into `target` (e.g. 'zh-CN' or 'en'); falls back to the
// original text on any failure so the UI never breaks.
async function translate(text, target) {
  if (!text) return text;
  const clean = text.slice(0, 800);
  const key = `${target}:${hash(clean)}`;
  if (memo.has(key)) return memo.get(key);
  try {
    const out = await gtxTranslate(clean, target);
    if (out) {
      memo.set(key, out);
      dirty = true;
      return out;
    }
  } catch (e) {
    /* graceful fallback below */
  }
  return text;
}

// Returns { en, zh } for a piece of text regardless of its source language.
async function toBilingual(text) {
  if (!text) return { en: '', zh: '' };
  if (hasCJK(text)) {
    return { zh: text, en: await translate(text, 'en') };
  }
  return { en: text, zh: await translate(text, 'zh-CN') };
}

module.exports = { translate, toBilingual, loadTranslationCache, flushTranslationCache };
