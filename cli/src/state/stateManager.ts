import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { SessionState } from '../types/index.js';

const HISTORY_FILE = path.join(os.homedir(), '.prof-history.json');

/**
 * StateManager for managing active sessions and conversation history.
 */
export class StateManager {
  private currentSession: SessionState | null = null;
  private history: Array<{ role: string, content: string, timestamp?: Date }> = [];

  constructor() {
    this.loadHistory();
  }

  createSession(): SessionState {
    this.currentSession = {
      sessionId: `session_${Date.now()}`,
      startTime: new Date(),
      history: [],
      context: new Map()
    };
    return this.currentSession;
  }

  getSession(): SessionState | null {
    return this.currentSession;
  }

  addToHistory(entry: { role: string, content: string }) {
    const historyEntry = { ...entry, timestamp: new Date() };
    this.history.push(historyEntry);
    if (this.currentSession) {
      this.currentSession.history.push(historyEntry as any);
    }
    this.saveHistory();
  }

  getHistory(): Array<{ role: string, content: string, timestamp?: Date }> {
    return this.history;
  }

  clearHistory() {
    this.history = [];
    if (this.currentSession) {
      this.currentSession.history = [];
    }
    this.saveHistory();
  }

  getContext(key: string): any {
    return this.currentSession?.context.get(key);
  }

  setContext(key: string, value: any) {
    this.currentSession?.context.set(key, value);
  }

  private loadHistory() {
    if (fs.existsSync(HISTORY_FILE)) {
      try {
        this.history = fs.readJsonSync(HISTORY_FILE);
      } catch (e) {
        this.history = [];
      }
    }
  }

  private saveHistory() {
    try {
      fs.writeJsonSync(HISTORY_FILE, this.history, { spaces: 2 });
    } catch (e) {
      // Ignore errors saving history
    }
  }
}

export const stateManager = new StateManager();
