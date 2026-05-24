/**
 * @module ui/components/banner
 * @description Renders the beautiful ASCII startup banner for Professor Profiler.
 * Combines figlet art, gradient coloring, and a boxen welcome card.
 */

import figlet from 'figlet';
import chalk from 'chalk';
import boxen from 'boxen';

import { getTheme, type ThemeConfig } from '../themes/index.js';

const CLI_VERSION = '1.0.0';
const DEFAULT_THEME = 'cyberpunk';

/**
 * Apply a line-by-line gradient using chalk to avoid multibyte character truncation issues
 */
function applyLineGradient(text: string, colors: string[]): string {
  if (!colors || colors.length === 0) return text;
  if (chalk.level < 3) return chalk.hex(colors[0])(text);
  
  const lines = text.split('\n');
  return lines
    .map((line, index) => {
      // Pick a color from the array cyclically, or map it linearly over the lines
      const colorIndex = Math.floor((index / Math.max(1, lines.length - 1)) * (colors.length - 1));
      const color = colors[colorIndex] || colors[colors.length - 1];
      return chalk.hex(color)(line);
    })
    .join('\n');
}

/**
 * Generate a figlet ASCII string.
 */
function renderAscii(text: string, font: string): Promise<string> {
  return new Promise((resolve, reject) => {
    figlet.text(text, { font: font as figlet.Fonts }, (err, data) => {
      if (err || !data) return reject(err);
      resolve(data);
    });
  });
}

/**
 * Construct the unified welcome card shown below the banner.
 */
function buildWelcomeCard(accentColor: string): string {
  const lines = [
    '',
    `  ${chalk.bold.white('Professor Profiler CLI')}  ${chalk.dim(`v${CLI_VERSION}`)}`,
    '',
    `  ${chalk.hex(accentColor)('◆')}  AI-Powered Exam Analysis`,
    `  ${chalk.hex(accentColor)('◆')}  Multi-Agent Document Profiling`,
    '',
    `  ${chalk.dim('Quick start:')}  ${chalk.white('prof analyze exam.pdf')}`,
    `  ${chalk.dim('All commands:')} ${chalk.white('prof --help')}`,
    '',
  ];

  return boxen(lines.join('\n'), {
    padding: { top: 0, bottom: 0, left: 1, right: 2 },
    margin: { top: 0, bottom: 0, left: 0, right: 0 },
    borderColor: chalk.level >= 3 ? accentColor : 'gray',
    borderStyle: 'round',
    float: 'left',
  });
}

/**
 * Display the CLI startup banner with dynamic theming.
 */
export async function showBanner(themeName?: string): Promise<void> {
  const theme = getTheme(themeName ?? DEFAULT_THEME);

  try {
    let ascii = await renderAscii(theme.bannerText, theme.figletFont);
    ascii = ascii.replace(/ +\n/g, '\n').replace(/ +$/g, '');

    console.log('');
    console.log(applyLineGradient(ascii, theme.gradientColors));

    console.log(buildWelcomeCard(theme.accentColor));
    console.log('');
  } catch {
    // Graceful fallback if figlet font is unavailable
    console.log('');
    console.log(applyLineGradient(`  ★  Professor Profiler CLI  v${CLI_VERSION}  ★`, theme.gradientColors));
    console.log('');
  }
}
