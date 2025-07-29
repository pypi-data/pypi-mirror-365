import ast

MAX_FUNC_LENGTH = 50  # Customize this if you want


def analyze_file(filepath):
    """
    Analyze a Python file from the filesystem.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
    return analyze_code(code, filepath)


def analyze_code(code, filename="<string>"):
    """
    Analyze raw Python source code (as string).
    """
    try:
        tree = ast.parse(code, filename=filename)
    except SyntaxError as e:
        return {
            "file": filename,
            "errors": [f"SyntaxError: {e}"],
            "issues": []
        }

    lines = code.splitlines()
    issues = []

    issues += check_duplicate_imports(tree)
    issues += check_unused_imports(tree)
    issues += check_unused_variables(tree)
    issues += check_long_functions(tree, lines)
    issues += check_todos_and_dead_code(lines)

    return {
        "file": filename,
        "errors": [],
        "issues": issues
    }


def check_duplicate_imports(tree):
    """
    Check for duplicate imports.
    """
    issues = []
    seen = set()
    duplicates = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                name = alias.name
                if name in seen:
                    duplicates.add(name)
                else:
                    seen.add(name)

    for name in duplicates:
        issues.append({
            "type": "DuplicateImport",
            "message": f"Duplicate import: {name}"
        })

    return issues


def check_unused_imports(tree):
    """
    Check for unused imports.
    """
    issues = []
    imports = set()
    used_names = set()

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                imports.add(alias.asname or alias.name.split('.')[0])
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                imports.add(alias.asname or alias.name)
            self.generic_visit(node)

        def visit_Name(self, node):
            used_names.add(node.id)

    ImportVisitor().visit(tree)

    unused = imports - used_names
    for name in unused:
        issues.append({
            "type": "UnusedImport",
            "message": f"Unused import: {name}"
        })

    return issues


def check_unused_variables(tree):
    """
    Check for unused variables.
    """
    assigned = set()
    used = set()
    issues = []

    class VarVisitor(ast.NodeVisitor):
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                assigned.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)

    VarVisitor().visit(tree)
    unused = assigned - used

    for var in unused:
        if not var.startswith("_"):
            issues.append({
                "type": "UnusedVariable",
                "message": f"Unused variable: {var}"
            })

    return issues


def check_long_functions(tree, lines):
    """
    Check for long functions.
    """
    issues = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start = node.lineno
            end = getattr(node, 'end_lineno', None)

            if not end:
                end = max(
                    (n.lineno for n in ast.walk(node) if hasattr(n, "lineno")),
                    default=start
                )

            length = end - start + 1
            if length > MAX_FUNC_LENGTH:
                issues.append({
                    "type": "LongFunction",
                    "message": f"Function '{node.name}' is too long ({length} lines)"
                })

    return issues


def check_todos_and_dead_code(lines):
    """
    Check for TODOs, FIXMEs, and dead/commented code blocks.
    """
    issues = []
    block_lines = []
    in_block = False

    for idx, line in enumerate(lines, 1):
        striped = line.strip().lower()

        if any(tag in striped for tag in ["todo", "fixme", "# hack"]):
            issues.append({
                "type": "TodoComment",
                "message": f'TODO/FIXME found at line {idx}: "{line.strip()}"'
            })

        if striped.startswith("#") and len(striped) > 8:
            block_lines.append(idx)
            in_block = True
        else:
            if in_block and len(block_lines) >= 5:
                issues.append({
                    "type": "DeadCode",
                    "message": f"{len(block_lines)} lines of commented-out code at lines {block_lines[0]}–{block_lines[-1]}"
                })
            block_lines = []
            in_block = False

    # In case the block ends at EOF
    if in_block and len(block_lines) >= 5:
        issues.append({
            "type": "DeadCode",
            "message": f"{len(block_lines)} lines of commented-out code at lines {block_lines[0]}–{block_lines[-1]}"
        })

    return issues
