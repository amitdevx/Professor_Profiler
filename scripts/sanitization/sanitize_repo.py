import os
import re

# Extensive emoji and decorative unicode pattern
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

# Box drawings and thick block characters using unicode escapes
THICK_LINES = re.compile(r'[\u2500-\u257f\u2580-\u259f\u25a0-\u25ff\u2190-\u21ff\u2600-\u26ff\u2700-\u27bf]+')
EMOJI_BULLETS = re.compile(r'^[ \t]*[\u2713\u2714\u2717\u2718\u26a0]+[ \t]*', re.MULTILINE)

modified_files = set()

def sanitize_content(content, filepath):
    original = content

    content = EMOJI_PATTERN.sub('', content)
    content = EMOJI_BULLETS.sub('', content)
    content = THICK_LINES.sub('', content)
    
    content = content.replace('\u2714', 'OK')
    content = content.replace('\u2716', 'ERR')
    content = content.replace('\u26a0', 'WARN')
    
    # Aggressively remove empty lines that result from stripping out emoji-only lines
    content = re.sub(r'^\s*$', '', content, flags=re.MULTILINE)

    if content != original:
        modified_files.add(filepath)
    return content

def process_repo(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.venv', 'dist', '__pycache__')]

        for filename in filenames:
            if not any(filename.endswith(ext) for ext in ['.py', '.ts', '.js', '.md', '.sh', '.json', '.yml', '.yaml']):
                continue
            
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                sanitized = sanitize_content(content, filepath)
                
                if filepath in modified_files:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(sanitized)
            except Exception as e:
                pass

if __name__ == '__main__':
    process_repo('.')
    print(f"Sanitized {len(modified_files)} files.")
