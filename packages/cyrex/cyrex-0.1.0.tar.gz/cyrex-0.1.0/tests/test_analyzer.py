from cyrex import analyzer

def test_unused_import_detection():
    code = "import os\nprint('Hello')"
    result = analyzer.analyze_code(code, "test_file.py")
    issues = result.get("issues", [])
    print(">>> UNUSED IMPORT ISSUES:", issues)  
    assert any("import" in i["message"].lower() for i in issues)


def test_todo_detection():
    code = "# TODO: fix this\nprint('Hi')"
    result = analyzer.analyze_code(code, "test_file.py")
    issues = result.get("issues", [])
    assert any("TODO" in i["message"] for i in issues)

def test_no_issues():
    code = "def add(a, b): return a + b"
    result = analyzer.analyze_code(code, "test_file.py")
    assert result.get("issues", []) == []

def test_long_function_detection():
    code = "def long():\n" + "\n".join(["    pass"] * 60)
    result = analyzer.analyze_code(code, "test_file.py")
    issues = result.get("issues", [])
    assert any("too long" in i["message"] for i in issues)

def test_dead_code_detection():
    code = "\n".join(["# comment line"] * 6)
    result = analyzer.analyze_code(code, "test_file.py")
    issues = result.get("issues", [])
    print(">>> DEAD CODE ISSUES:", issues)  # 
    assert any("comment" in i["message"].lower() for i in issues)
