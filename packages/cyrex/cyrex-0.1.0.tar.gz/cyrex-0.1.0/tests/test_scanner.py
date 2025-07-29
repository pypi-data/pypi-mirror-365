from cyrex import scanner
import tempfile
import os

def test_scanner_finds_python_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "demo.py")
        with open(filepath, "w") as f:
            f.write("print('hello')")
        files = scanner.get_python_files(tmpdir)
        from pathlib import Path
        assert Path(filepath) in files