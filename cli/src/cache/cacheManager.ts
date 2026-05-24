import fs from 'fs-extra';
import path from 'path';
import os from 'os';

const CACHE_FILE = path.join(os.homedir(), '.prof-cache.json');

interface CacheEntry<T> {
  value: T;
  timestamp: number;
  ttlMs: number | null;
}

export class CacheManager {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private hits = 0;
  private misses = 0;

  constructor() {
    this.load();
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) {
      this.misses++;
      return null;
    }
    
    if (entry.ttlMs !== null && Date.now() - entry.timestamp > entry.ttlMs) {
      this.cache.delete(key);
      this.misses++;
      this.save();
      return null;
    }

    this.hits++;
    return entry.value as T;
  }

  set<T>(key: string, value: T, ttlMs: number | null = null): void {
    this.cache.set(key, { value, timestamp: Date.now(), ttlMs });
    this.save();
  }

  has(key: string): boolean {
    return this.get(key) !== null;
  }

  invalidate(key: string): void {
    this.cache.delete(key);
    this.save();
  }

  clear(): void {
    this.cache.clear();
    this.save();
  }

  getStats(): { hits: number; misses: number; size: number } {
    return { hits: this.hits, misses: this.misses, size: this.cache.size };
  }

  private load() {
    if (fs.existsSync(CACHE_FILE)) {
      try {
        const data = fs.readJsonSync(CACHE_FILE);
        this.cache = new Map(Object.entries(data));
      } catch (e) {
        this.cache = new Map();
      }
    }
  }

  private save() {
    try {
      fs.writeJsonSync(CACHE_FILE, Object.fromEntries(this.cache), { spaces: 2 });
    } catch (e) {
      // Ignore
    }
  }
}

export const cacheManager = new CacheManager();
