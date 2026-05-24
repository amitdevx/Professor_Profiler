/**
 * @module ui/themes
 * @description ASCII theme system for Professor Profiler CLI.
 * Provides curated visual themes that control the startup banner,
 * gradient palettes, accent colors, and spinner styles.
 */

/**
 * Spinner style names recognized by the `ora` spinner library.
 */
export type SpinnerStyle =
  | 'dots'
  | 'dots2'
  | 'line'
  | 'star'
  | 'hamburger'
  | 'bouncingBar'
  | 'arc'
  | 'squareCorners'
  | 'circleHalves'
  | 'aesthetic';

/**
 * A complete visual theme definition for the CLI.
 */
export interface Theme {
  /** Human-readable theme name. */
  name: string;
  /** Short description shown in theme listings. */
  description: string;
  /** ASCII banner text rendered by figlet. */
  bannerText: string;
  /** Figlet font for banner rendering. */
  figletFont: string;
  /** Hex color array for `gradient-string`. */
  gradientColors: string[];
  /** Primary accent hex color for highlights. */
  accentColor: string;
  /** Secondary accent hex color for subtle elements. */
  secondaryColor: string;
  /** Ora spinner style key. */
  spinnerStyle: SpinnerStyle;
  /** Border style for boxen cards. */
  borderStyle: 'round' | 'bold' | 'double' | 'single' | 'classic';
}

/**
 * Minimal — clean, modern, no-nonsense startup.
 */
const minimal: Theme = {
  name: 'minimal',
  description: 'Clean and modern — no distractions',
  bannerText: 'PROF',
  figletFont: 'ANSI Shadow',
  gradientColors: ['#667eea', '#764ba2'],
  accentColor: '#667eea',
  secondaryColor: '#a78bfa',
  spinnerStyle: 'dots',
  borderStyle: 'round',
};

/**
 * Cyberpunk — neon gradients, futuristic vibes.
 */
const cyberpunk: Theme = {
  name: 'cyberpunk',
  description: 'Neon gradients — futuristic terminal aesthetic',
  bannerText: 'PROF',
  figletFont: 'ANSI Shadow',
  gradientColors: ['#f72585', '#b5179e', '#7209b7', '#560bad', '#480ca8', '#3a0ca3', '#3f37c9', '#4361ee', '#4895ef', '#4cc9f0'],
  accentColor: '#f72585',
  secondaryColor: '#4cc9f0',
  spinnerStyle: 'arc',
  borderStyle: 'double',
};

/**
 * Hacker — Matrix-inspired green-on-black.
 */
const hacker: Theme = {
  name: 'hacker',
  description: 'Matrix-style green — for the terminal purist',
  bannerText: 'PROF',
  figletFont: 'ANSI Shadow',
  gradientColors: ['#00ff41', '#00cc33', '#009926', '#006619', '#00ff41'],
  accentColor: '#00ff41',
  secondaryColor: '#33ff77',
  spinnerStyle: 'line',
  borderStyle: 'bold',
};

/**
 * Ocean — calm deep-sea blues with warm highlights.
 */
const ocean: Theme = {
  name: 'ocean',
  description: 'Deep-sea blues — calm and professional',
  bannerText: 'PROF',
  figletFont: 'ANSI Shadow',
  gradientColors: ['#0077b6', '#0096c7', '#00b4d8', '#48cae4', '#90e0ef', '#ade8f4'],
  accentColor: '#00b4d8',
  secondaryColor: '#90e0ef',
  spinnerStyle: 'dots2',
  borderStyle: 'round',
};

/**
 * Sunset — warm gradient from gold to rose.
 */
const sunset: Theme = {
  name: 'sunset',
  description: 'Warm golds and roses — rich and inviting',
  bannerText: 'PROF',
  figletFont: 'ANSI Shadow',
  gradientColors: ['#ff6b35', '#f7c59f', '#efefd0', '#004e89', '#1a659e'],
  accentColor: '#ff6b35',
  secondaryColor: '#f7c59f',
  spinnerStyle: 'star',
  borderStyle: 'round',
};

/**
 * Internal theme registry keyed by name.
 */
const themes: Record<string, Theme> = {
  minimal,
  cyberpunk,
  hacker,
  ocean,
  sunset,
};

/**
 * Retrieve a theme by name.
 * Falls back to `minimal` if the requested name is not found.
 *
 * @param name - Theme identifier (case-insensitive).
 * @returns The resolved {@link Theme} object.
 *
 * @example
 * ```ts
 * const theme = getTheme('cyberpunk');
 * console.log(theme.gradientColors);
 * ```
 */
export function getTheme(name: string): Theme {
  const key = name.toLowerCase().trim();
  return themes[key] ?? themes['minimal']!;
}

/**
 * List every registered theme with its name and description.
 *
 * @returns An array of `{ name, description }` objects.
 */
export function listThemes(): Array<{ name: string; description: string }> {
  return Object.values(themes).map((t) => ({
    name: t.name,
    description: t.description,
  }));
}

/**
 * The default theme used when no override is provided.
 */
export const DEFAULT_THEME = 'cyberpunk';
