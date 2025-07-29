#!/usr/bin/env python3
import os
import sys
import glob
import requests
import json
import pytest
import hashlib
import pickle
from pathlib import Path

API_KEY = os.getenv('ANTHROPIC_API_KEY')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'

if not API_KEY:
    print('Error: ANTHROPIC_API_KEY environment variable not set.')
    sys.exit(1)

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

PYTHONPATH_FIX = (
    "import sys\n"
    "import os\n"
    "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
)

def get_file_hash(file_path):
    """Generate a hash of file content and modification time."""
    try:
        stat = os.stat(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        # Combine content hash with modification time
        content_hash = hashlib.md5(content).hexdigest()
        return f"{content_hash}_{stat.st_mtime}"
    except (OSError, IOError):
        return None

def get_cache_file_path(app_path):
    """Get the path to the cache file for storing file hashes."""
    return os.path.join(app_path, '.test_generator_cache')

def load_file_cache(app_path):
    """Load the cached file hashes."""
    cache_file = get_cache_file_path(app_path)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError):
            return {}
    return {}

def save_file_cache(app_path, file_hashes):
    """Save the file hashes to cache."""
    cache_file = get_cache_file_path(app_path)
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(file_hashes, f)
    except (OSError, IOError) as e:
        print(f"Warning: Could not save cache file: {e}")

def check_files_changed(app_path):
    """Check if any Python files have changed since last run."""
    py_files = get_python_files(app_path)
    if not py_files:
        return True, []  # No files found, consider as changed
    
    cached_hashes = load_file_cache(app_path)
    current_hashes = {}
    changed_files = []
    
    for file_path in py_files:
        current_hash = get_file_hash(file_path)
        if current_hash is None:
            continue
            
        current_hashes[file_path] = current_hash
        
        # Check if file is new or has changed
        if file_path not in cached_hashes or cached_hashes[file_path] != current_hash:
            changed_files.append(file_path)
    
    # Check for deleted files
    for cached_file in cached_hashes:
        if cached_file not in current_hashes and os.path.exists(cached_file):
            changed_files.append(cached_file)
    
    # Save current hashes for next run
    save_file_cache(app_path, current_hashes)
    
    return len(changed_files) > 0, changed_files

def get_python_files(app_path):
    """Get all Python files in the app directory, excluding tests directory and generated test files."""
    all_py_files = [y for x in os.walk(app_path) for y in glob.glob(os.path.join(x[0], '*.py'))]
    
    # Filter out files in tests directory and generated test files
    filtered_files = []
    for file_path in all_py_files:
        # Skip files in tests directory
        if 'tests' in file_path.split(os.sep):
            continue
        # Skip generated test files (files starting with test_)
        if os.path.basename(file_path).startswith('test_'):
            continue
        filtered_files.append(file_path)
    
    return filtered_files

def read_files(file_paths):
    code = ''
    for path in file_paths:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            code += f'\n# File: {path}\n' + f.read() + '\n'
    return code

def generate_test_cases(code):
    headers = {
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }
    prompt = (
        "You are an expert Python developer and QA engineer. "
        "Given the following Python application code, write comprehensive unit tests for it. "
        "Use pytest style. Output only the test code, no explanations. "
        "If the code is too large, focus on the most important functions/classes.\n"
        f"\n{code}\n"
    )
    data = {
        "model": "claude-3-5-sonnet-20241022",  # You can change to another Claude model if needed
        "max_tokens": 2048,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(CLAUDE_API_URL, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print('Error from Claude API:', response.status_code, response.text)
        sys.exit(1)
    result = response.json()
    # Claude's response format may vary; adjust as needed
    return result.get('content', result)

def clean_test_code(test_code):
    # Remove triple backticks and ```python from start/end
    lines = test_code.strip().splitlines()
    # Remove leading code block markers
    while lines and (lines[0].strip() == '```' or lines[0].strip() == '```python'):
        lines.pop(0)
    # Remove trailing code block markers
    while lines and lines[-1].strip() == '```':
        lines.pop()
    return '\n'.join(lines).strip()

def write_test_files(app_path, py_files, test_cases):
    tests_dir = os.path.join(app_path, 'tests')
    os.makedirs(tests_dir, exist_ok=True)
    if isinstance(test_cases, list):
        test_texts = [obj.get('text', '') for obj in test_cases]
    elif isinstance(test_cases, str):
        test_texts = [test_cases]
    else:
        test_texts = [str(test_cases)]
    # Clean up code blocks
    test_texts = [clean_test_code(tc) for tc in test_texts]
    if len(py_files) == len(test_texts):
        for src, test_code in zip(py_files, test_texts):
            src_name = os.path.basename(src)
            test_file = os.path.join(tests_dir, f'test_{src_name}')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(PYTHONPATH_FIX + test_code + '\n')
    else:
        test_file = os.path.join(tests_dir, 'test_generated.py')
        with open(test_file, 'w', encoding='utf-8') as f:
            for test_code in test_texts:
                f.write(PYTHONPATH_FIX + test_code + '\n')

@pytest.fixture
def temp_tasks_file(tmp_path, monkeypatch):
    temp_file = tmp_path / "tasks.json"
    # Patch the path in your app to use this temp file
    monkeypatch.setattr("notes_app.storage.TASKS_FILE", str(temp_file))
    return str(temp_file)

def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} /path/to/python/app')
        sys.exit(1)
    app_path = sys.argv[1]
    if not os.path.isdir(app_path):
        print(f'Error: {app_path} is not a directory')
        sys.exit(1)
    
    # Check if any files have changed
    files_changed, changed_files = check_files_changed(app_path)
    
    if not files_changed:
        print("✅ No changes detected in your code. Skipping API call to save costs.")
        print("If you want to regenerate tests anyway, delete the .test_generator_cache file and run again.")
        return
    
    if changed_files:
        print(f"📝 Detected changes in {len(changed_files)} file(s):")
        for file_path in changed_files:
            print(f"   - {os.path.relpath(file_path, app_path)}")
        print()
    
    py_files = get_python_files(app_path)
    if not py_files:
        print('No Python files found in the specified directory.')
        sys.exit(1)
    code = read_files(py_files)
    print('Generating test cases using Claude...')
    test_cases = generate_test_cases(code)
    print('Writing test cases to tests/ directory...')
    write_test_files(app_path, py_files, test_cases)
    print('Test cases written to tests/ directory.')

if __name__ == '__main__':
    main() 