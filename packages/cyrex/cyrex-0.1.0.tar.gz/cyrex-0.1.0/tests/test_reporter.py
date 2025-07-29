import os
import json
import tempfile
from cyrex import reporter

def test_save_json_report_creates_valid_file():
    test_data = {
        "file": [
            {"type": "unused_import", "line": 5, "details": "import os"}
        ]
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_report.json")
        reporter.save_json_report(test_data, output_path)

        assert os.path.exists(output_path), "Report file was not created."

        with open(output_path, "r") as f:
            loaded = json.load(f)
            assert loaded == test_data, "Report data mismatch."

def test_cli_report_output(capfd):
    # Simulate a simple in-memory report
    report = {
        "example.py": [
            {"type": "unused_import", "line": 2, "details": "import os"},
            {"type": "todo_comment", "line": 10, "details": "# TODO: fix this"}
        ]
    }

    reporter.print_cli_report(report)

    out, err = capfd.readouterr()
    assert "example.py" in out
    assert "import os" in out
    assert "TODO" in out
