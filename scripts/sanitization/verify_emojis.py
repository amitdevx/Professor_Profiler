import os
import re
import sys

# Unicode ranges corresponding to emojis and decorative characters
EMOJI_PATTERN = re.compile(
    r'['
    r'\U00010000-\U0010ffff' # SMP (emojis, etc.)
    r'\u2600-\u27bf' # Misc symbols
    r'\u2300-\u23ff' # Tech symbols
    r'\u2b50\u2b55'  # Stars
    r'\u2934-\u2935' # Arrows
    r'\u25b6\u25c0'  # Play buttons
    r'\u2139\u2122'  # Info, TM
    r'\u3297\u3299'  # Circled ideographs
    r'\u24c2'        # Circled M
    r'\u25aa-\u25ab\u25fb-\u25fe' # Small squares
    r'\u2714\u2716\u2718' # Checkmarks, crosses
    r']+', 
    flags=re.UNICODE
)

def verify():
    findings = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'dist', '__pycache__')]
        for filename in filenames:
            if not any(filename.endswith(ext) for ext in ['.py', '.ts', '.js', '.md', '.sh', '.json', '.yml', '.yaml']):
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        match = EMOJI_PATTERN.search(line)
                        if match:
                            print(f"{filepath}:{i} => {match.group(0)} in text: {line.strip()}")
                            findings += 1
            except Exception:
                pass
    return findings

if __name__ == '__main__':
    count = verify()
    if count > 0:
        print(f"FAILED: Found {count} emojis/decorative unicode.")
        sys.exit(1)
    else:
        print("PASS: No emojis or decorative unicode found.")
        sys.exit(0)
