import { ProfSDK } from '../sdk/index.js';

export interface Plugin {
  name: string;
  version: string;
  initialize(sdk: ProfSDK): Promise<void>;
  dispose(): Promise<void>;
}

export class PluginManager {
  private plugins: Map<string, Plugin> = new Map();

  async register(plugin: Plugin, sdk: ProfSDK): Promise<void> {
    await plugin.initialize(sdk);
    this.plugins.set(plugin.name, plugin);
  }

  async unregister(pluginName: string): Promise<void> {
    const plugin = this.plugins.get(pluginName);
    if (plugin) {
      await plugin.dispose();
      this.plugins.delete(pluginName);
    }
  }

  list(): Plugin[] {
    return Array.from(this.plugins.values());
  }
}
