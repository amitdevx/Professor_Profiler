import os
import re

noisy_prefixes = [
    'step', 'initialize', 'create', 'update', 'delete', 'remove', 'ensure',
    'check', 'test', 'parse', 'extract', 'sort', 'build', 'handle', 'setup',
    'add', 'get', 'set', 'return', 'show', 'print', 'run', 'execute', 'simulate',
    'determine', 'formulate', 'save', 'look', 'find', 'import', 'define',
    'container', 'format', 'convert', 'use', 'start', 'end', 'cleanup', 'clear',
    'search', 'retrieve', 'filter', 'calculate', 'return appropriate', 'try',
    'let', 'main', 'fallback for', 'prevent'
]

noisy_exact = ['ignore', 'setup', 'cleanup', 'test', 'run', 'main loop']

def is_noisy_comment(text):
    text = text.strip()
    clean_text = re.sub(r'^(\s*(//|#)\s*)', '', text).strip().lower()
    
    if not clean_text: return False
    if any(clean_text.startswith(p) for p in noisy_prefixes): return True
    if clean_text in noisy_exact: return True
    if re.match(r'^[-=_\*\/]+$', clean_text): return True
    if clean_text.startswith('this function') or clean_text.startswith('this method') or clean_text.startswith('this class'): return True
    return False

def sanitize_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        new_lines = []
        modified = False
        is_ts_js = filepath.endswith('.ts') or filepath.endswith('.js')
        is_py = filepath.endswith('.py')

        for line in lines:
            stripped = line.strip()
            
            # Only process pure single line comments
            if is_ts_js and stripped.startswith('//'):
                if is_noisy_comment(stripped):
                    modified = True
                    continue
            elif is_py and stripped.startswith('#') and not stripped.startswith('#!'):
                if is_noisy_comment(stripped):
                    modified = True
                    continue
                    
            if re.match(r'^\s*console\.log\([\'"]\s*[\-=_\*]{5,}\s*[\'"]\);?\s*$', line):
                modified = True
                continue
                
            new_lines.append(line)
            
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    count = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'dist', '__pycache__')]
        for filename in filenames:
            if not any(filename.endswith(ext) for ext in ['.py', '.ts', '.js']):
                continue
            filepath = os.path.join(dirpath, filename)
            if sanitize_file(filepath):
                print(f"Sanitized comments in: {filepath}")
                count += 1
    print(f"Sanitized comments in {count} files.")

if __name__ == '__main__':
    main()
