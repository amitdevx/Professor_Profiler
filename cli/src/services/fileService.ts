/**
 * @module services/fileService
 * @description Handles @ file path resolution, validation, and copy-to-processing.
 * Central service for all file operations in the CLI.
 */

import path from 'node:path';
import fs from 'fs-extra';
import ora from 'ora';
import chalk from 'chalk';

import type { FileInfo } from '../types/index.js';
import { eventBus } from '../core/events.js';

/**
 * Supported file extensions and their human-readable type names.
 */
const FILE_TYPE_MAP: Record<string, string> = {
  '.pdf': 'PDF Document',
  '.md': 'Markdown File',
  '.txt': 'Plain Text',
  '.docx': 'Word Document',
  '.doc': 'Word Document (Legacy)',
  '.csv': 'CSV Spreadsheet',
  '.json': 'JSON Data',
};

/**
 * Extensions that are accepted for analysis.
 */
const SUPPORTED_EXTENSIONS = new Set(['.pdf', '.md', '.txt', '.docx', '.doc', '.json', '.py', '.ts', '.js']);

/**
 * File handling service for the Professor Profiler CLI.
 * Manages path resolution, validation, and file operations.
 */
export class FileService {
  /**
   * Resolve a user-supplied file path.
   *
   * Handles the `@` prefix convention (e.g. `@exam.pdf` → `./exam.pdf`),
   * resolves relative paths against the current working directory,
   * and populates a {@link FileInfo} object.
   *
   * @param input - Raw user input (may include `@` prefix).
   * @returns A populated {@link FileInfo} object.
   *
   * @example
   * ```ts
   * const info = fileService.resolveFilePath('@notes.md');
   * console.log(info.path); // /home/user/notes.md
   * ```
   */
  resolveFilePath(input: string): FileInfo {
    // Strip @ prefix if present
    const cleaned = input.startsWith('@') ? input.slice(1) : input;

    // Resolve to absolute path
    const absolutePath = path.resolve(process.cwd(), cleaned);
    const ext = path.extname(absolutePath).toLowerCase();
    const name = path.basename(absolutePath);

    let size = 0;
    try {
      const stat = fs.statSync(absolutePath);
      size = stat.size;
    } catch {
      // File may not exist yet — that's checked in validateFile
    }

    const fileInfo: FileInfo = {
      name,
      path: absolutePath,
      size,
      type: this.getFileType(ext),
      resolvedAt: new Date(),
    };

    // Emit resolution event
    eventBus.emit('file:resolved', { fileInfo } as any);

    return fileInfo;
  }

  /**
   * Validate that a file exists and has a supported extension.
   *
   * @param fileInfo - The {@link FileInfo} to validate.
   * @returns An object with `valid` (boolean) and optional `error` message.
   */
  validateFile(fileInfo: FileInfo): { valid: boolean; error?: string } {
    // Check existence
    if (!fs.existsSync(fileInfo.path)) {
      return {
        valid: false,
        error: `File not found: ${fileInfo.path}`,
      };
    }

    // Check it's actually a file (not directory)
    const stat = fs.statSync(fileInfo.path);
    if (!stat.isFile()) {
      return {
        valid: false,
        error: `Path is not a file: ${fileInfo.path}`,
      };
    }

    // Check extension
    const ext = path.extname(fileInfo.path).toLowerCase();
    if (!SUPPORTED_EXTENSIONS.has(ext)) {
      const supported = [...SUPPORTED_EXTENSIONS].join(', ');
      return {
        valid: false,
        error: `Unsupported file type "${ext}". Supported: ${supported}`,
      };
    }

    // Check file is not empty
    if (stat.size === 0) {
      return {
        valid: false,
        error: `File is empty: ${fileInfo.name}`,
      };
    }

    return { valid: true };
  }

  /**
   * Copy a file to the processing directory with an upload animation.
   *
   * @param fileInfo - The source {@link FileInfo}.
   * @param destDir  - Destination directory (e.g. `../input/`).
   * @returns The absolute path of the copied file.
   *
   * @example
   * ```ts
   * const dest = await fileService.copyToProcessing(info, '../input');
   * ```
   */
  async copyToProcessing(fileInfo: FileInfo, destDir: string): Promise<string> {
    const resolvedDest = path.resolve(process.cwd(), destDir);

    // Ensure destination directory exists
    await fs.ensureDir(resolvedDest);

    const destPath = path.join(resolvedDest, fileInfo.name);

    const spinner = ora({
      text: chalk.cyan(`Uploading ${chalk.bold(fileInfo.name)} to processing folder...`),
      spinner: 'dots',
    }).start();

    try {
      await fs.copy(fileInfo.path, destPath, { overwrite: true });

      // Brief delay for visual feedback
      await new Promise((r) => setTimeout(r, 400));

      const sizeKB = (fileInfo.size / 1024).toFixed(1);
      spinner.succeed(
        chalk.green(`Uploaded ${chalk.bold(fileInfo.name)} (${sizeKB} KB) → ${chalk.dim(resolvedDest)}`),
      );

      return destPath;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      spinner.fail(chalk.red(`Failed to copy ${fileInfo.name}: ${errorMessage}`));
      throw err;
    }
  }

  /**
   * Read text content from a file.
   * For PDF, doc, and docx, runs a Python subprocess (using virtualenv python if present)
   * to parse using backend tools. For other extensions, reads using fs.readFile.
   */
  async readFileText(fileInfo: FileInfo): Promise<string> {
    const ext = path.extname(fileInfo.path).toLowerCase();
    if (ext === '.pdf' || ext === '.docx' || ext === '.doc') {
      const { fileURLToPath } = await import('node:url');
      const __dirname = path.dirname(fileURLToPath(import.meta.url));
      const repoRoot = path.resolve(__dirname, '../../');
      
      const venvPython = path.resolve(repoRoot, '.venv/bin/python');
      const pythonExec = fs.existsSync(venvPython) ? venvPython : 'python3';

      const script = `import sys; sys.path.insert(0, '${repoRoot}'); from profiler_agent.tools import read_pdf_content; import json; print(json.dumps(read_pdf_content('${fileInfo.path}')))`;
      const { execSync } = await import('node:child_process');
      const result = execSync(`"${pythonExec}" -c "${script}"`, { stdio: ['pipe', 'pipe', 'ignore'] }).toString();
      const parsed = JSON.parse(result);
      if (parsed.error) throw new Error(parsed.error);
      return parsed.content;
    }
    return await fs.readFile(fileInfo.path, 'utf-8');
  }

  /**
   * Map a file extension to its human-readable type name.
   *
   * @param ext - The file extension (including leading dot).
   * @returns Human-readable type string.
   */
  getFileType(ext: string): string {
    return FILE_TYPE_MAP[ext.toLowerCase()] ?? 'Unknown';
  }
}

/**
 * Pre-instantiated singleton.
 */
export const fileService = new FileService();
