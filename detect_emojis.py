import os
import re
import sys

def contains_emoji(text):
    # Match a wide range of emojis and symbols
    # Exclude basic ASCII and common Latin characters
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50\u2b55\u2934-\u2935\u25b6\u25c0\u2139\u2122\u3297\u3299\u24c2\u25aa-\u25ab\u25fb-\u25fe]', flags=re.UNICODE)
    return emoji_pattern.search(text) is not None

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if contains_emoji(line):
                    print(f"{filepath}:{i}: {line.strip()}")
    except UnicodeDecodeError:
        pass
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

def main():
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude directories
        if '.git' in dirnames: dirnames.remove('.git')
        if 'node_modules' in dirnames: dirnames.remove('node_modules')
        if '.venv' in dirnames: dirnames.remove('.venv')
        if 'dist' in dirnames: dirnames.remove('dist')
        if '__pycache__' in dirnames: dirnames.remove('__pycache__')

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            scan_file(filepath)

if __name__ == "__main__":
    main()
