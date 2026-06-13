// Minimal in-memory cache with per-key TTL. Used to respect free-tier rate
// limits by serving aggregated results from memory between refreshes.
class TTLCache {
  constructor() {
    this.store = new Map();
  }

  get(key) {
    const entry = this.store.get(key);
    if (!entry) return undefined;
    if (entry.expiry && entry.expiry < Date.now()) {
      this.store.delete(key);
      return undefined;
    }
    return entry.value;
  }

  set(key, value, ttlMs) {
    this.store.set(key, { value, expiry: ttlMs ? Date.now() + ttlMs : 0 });
  }
}

module.exports = { TTLCache };
