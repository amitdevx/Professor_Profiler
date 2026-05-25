/**
 * @module commands/doctor
 * @description The `prof doctor` command — comprehensive environment health check.
 * Validates Node.js version, Python availability, .venv, API keys,
 * terminal capabilities, and output directories.
 */

import { Command } from 'commander';
import { execSync } from 'node:child_process';
import path from 'node:path';
import fs from 'fs-extra';
import boxen from 'boxen';
import chalk from 'chalk';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../../');

/**
 * Result of a single diagnostic check.
 */
interface CheckResult {
  /** Check display label. */
  label: string;
  /** Whether the check passed. */
  passed: boolean;
  /** Detailed message. */
  message: string;
  /** Severity: pass, fail, or warn. */
  severity: 'pass' | 'fail' | 'warn';
}

/**
 * Run a single diagnostic check.
 */
type CheckFn = () => CheckResult;

/**
 * Icons for each severity level.
 */
const ICONS = {
  pass: chalk.green('✓'),
  fail: chalk.red('✗'),
  warn: chalk.yellow('⚠'),
};

/**
 * Check Node.js version (require 18+).
 */
function checkNodeVersion(): CheckResult {
  const version = process.version;
  const major = parseInt(version.replace('v', '').split('.')[0]!, 10);

  return {
    label: 'Node.js',
    passed: major >= 18,
    message: major >= 18 ? `${version} (meets requirement ≥ 18)` : `${version} — requires Node.js 18+`,
    severity: major >= 18 ? 'pass' : 'fail',
  };
}

/**
 * Check Python 3 availability.
 */
function checkPython(): CheckResult {
  try {
    const version = execSync('python3 --version 2>&1', { encoding: 'utf-8' }).trim();
    return { label: 'Python 3', passed: true, message: version, severity: 'pass' };
  } catch {
    return {
      label: 'Python 3',
      passed: false,
      message: 'Not found — required for the agent backend',
      severity: 'fail',
    };
  }
}

/**
 * Check if .venv exists in the parent directory.
 */
function checkVenv(): CheckResult {
  const venvPath = path.join(repoRoot, '.venv');
  const exists = fs.existsSync(venvPath);

  return {
    label: 'Virtual Env (.venv)',
    passed: exists,
    message: exists ? `Found at ${venvPath}` : `Not found at ${venvPath}`,
    severity: exists ? 'pass' : 'warn',
  };
}

/**
 * Check for API keys in .env file.
 */
function checkApiKeys(): CheckResult {
  const envPath = path.join(repoRoot, '.env');

  if (!fs.existsSync(envPath)) {
    return {
      label: 'API Keys (.env)',
      passed: false,
      message: `No .env file found at ${envPath}`,
      severity: 'warn',
    };
  }

  const content = fs.readFileSync(envPath, 'utf-8');
  const keys = ['GOOGLE_API_KEY', 'NIM_API_KEY', 'NVIDIA_API_KEY'];
  const found = keys.filter((k) => content.includes(k));

  if (found.length === 0) {
    return {
      label: 'API Keys (.env)',
      passed: false,
      message: 'No API keys configured',
      severity: 'warn',
    };
  }

  return {
    label: 'API Keys (.env)',
    passed: true,
    message: `${found.length} key(s) configured: ${found.join(', ')}`,
    severity: 'pass',
  };
}

/**
 * Check terminal capabilities.
 */
function checkTerminal(): CheckResult {
  const isTTY = !!process.stdout.isTTY;
  const columns = process.stdout.columns ?? 80;
  const colorSupport = chalk.level > 0;

  const parts: string[] = [];
  if (isTTY) parts.push('TTY');
  if (colorSupport) parts.push(`Color Level ${chalk.level}`);
  parts.push(`${columns} columns`);

  return {
    label: 'Terminal',
    passed: isTTY && colorSupport,
    message: parts.join(', '),
    severity: isTTY && colorSupport ? 'pass' : 'warn',
  };
}

/**
 * Check output directories.
 */
function checkOutputDirs(): CheckResult {
  const dirs = ['output', 'output/reports', 'output/charts'].map(d => path.join(repoRoot, d));
  const existing = dirs.filter((d) => fs.existsSync(d));

  if (existing.length === dirs.length) {
    return {
      label: 'Output Directories',
      passed: true,
      message: `All ${dirs.length} directories present`,
      severity: 'pass',
    };
  }

  return {
    label: 'Output Directories',
    passed: false,
    message: `${existing.length}/${dirs.length} directories found (missing will be created on first run)`,
    severity: 'warn',
  };
}

/**
 * All diagnostic checks.
 */
const CHECKS: CheckFn[] = [
  checkNodeVersion,
  checkPython,
  checkVenv,
  checkApiKeys,
  checkTerminal,
  checkOutputDirs,
];

/**
 * Create and return the `doctor` command.
 *
 * **Usage:** `prof doctor`
 *
 * @returns A configured Commander {@link Command} object.
 */
export function createDoctorCommand(): Command {
  const cmd = new Command('doctor')
    .description('Check your environment for Professor Profiler compatibility')
    .action(() => {
      console.log('');
      console.log(chalk.bold.white('  🏥 Professor Profiler — Environment Check'));
      console.log(chalk.dim('  ───────────────────────────────────────────'));
      console.log('');

      const results: CheckResult[] = [];

      for (const check of CHECKS) {
        const result = check();
        results.push(result);

        const icon = ICONS[result.severity];
        const label = chalk.white(result.label.padEnd(24));
        const message = result.severity === 'pass'
          ? chalk.green(result.message)
          : result.severity === 'warn'
            ? chalk.yellow(result.message)
            : chalk.red(result.message);

        console.log(`  ${icon}  ${label} ${message}`);
      }

      console.log('');

      // Summary card
      const passed = results.filter((r) => r.severity === 'pass').length;
      const warned = results.filter((r) => r.severity === 'warn').length;
      const failed = results.filter((r) => r.severity === 'fail').length;

      let summaryColor: string;
      let summaryIcon: string;
      let summaryText: string;

      if (failed > 0) {
        summaryColor = 'red';
        summaryIcon = '✖';
        summaryText = `${failed} check(s) failed. Fix the issues above before proceeding.`;
      } else if (warned > 0) {
        summaryColor = 'yellow';
        summaryIcon = '⚠';
        summaryText = `All critical checks passed. ${warned} warning(s) to review.`;
      } else {
        summaryColor = 'green';
        summaryIcon = '✔';
        summaryText = 'All checks passed! Your environment is ready.';
      }

      const card = boxen(
        [
          '',
          `  ${chalk.hex(summaryColor === 'red' ? '#ff0000' : summaryColor === 'yellow' ? '#ffaa00' : '#00ff41').bold(`${summaryIcon}  ${summaryText}`)}`,
          '',
          `  ${chalk.green(`${passed} passed`)}  ${chalk.yellow(`${warned} warnings`)}  ${chalk.red(`${failed} failed`)}`,
          '',
        ].join('\n'),
        {
          padding: { top: 0, bottom: 0, left: 1, right: 1 },
          borderColor: summaryColor as any,
          borderStyle: 'round',
          title: ' Summary ',
          titleAlignment: 'center',
        },
      );

      console.log(card);
      console.log('');
    });

  return cmd;
}
