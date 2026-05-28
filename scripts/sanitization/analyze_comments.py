import os
import re

ts_comment_re = re.compile(r'^\s*//\s*(.*)$')
py_comment_re = re.compile(r'^\s*#\s*(.*)$')
block_comment_start = re.compile(r'^\s*/\*\*?')

def analyze():
    for dirpath, dirnames, filenames in os.walk('.'):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'dist', '__pycache__')]
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            is_ts = filename.endswith('.ts') or filename.endswith('.js')
            is_py = filename.endswith('.py')
            if not is_ts and not is_py: continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if is_ts:
                        m = ts_comment_re.match(line)
                        if m: print(f"{filepath}:{i}: {line.strip()}")
                        if block_comment_start.match(line):
                            print(f"{filepath}:{i}: {line.strip()} (Block comment)")
                    elif is_py:
                        m = py_comment_re.match(line)
                        if m and not line.strip().startswith('#!'):
                            print(f"{filepath}:{i}: {line.strip()}")
            except Exception:
                pass

if __name__ == '__main__':
    analyze()
