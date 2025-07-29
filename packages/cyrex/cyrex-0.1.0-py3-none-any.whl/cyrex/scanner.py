from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", ".git", "venv", ".venv"}

def get_python_files(base_path="."):
    files = []
    for path in Path(base_path).rglob("*.py"):
        if not any(part in EXCLUDE_DIRS for part in path.parts):
            files.append(path)
    return files
