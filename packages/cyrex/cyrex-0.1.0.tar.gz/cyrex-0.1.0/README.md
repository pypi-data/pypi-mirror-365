#  cyrex – Minimal Static Code Analyzer for Python

> A lightweight CLI tool to scan Python projects and catch common hygiene issues — no AI, no cloud, just clean code.

---

##  Overview

`cyrex` is a developer-friendly, blazing-fast static analysis tool for Python codebases.  
It scans your project and reports:

-  Unused imports and variables  
-  Duplicate imports  
-  TODO / FIXME / HACK comments  
-  Overly long functions  
-  Commented-out (dead) code blocks  

All results are shown in a colorful CLI using [`rich`], with an optional JSON report for automation or CI.

---

##  Features

| Check Type             | Description                                              |
|------------------------|----------------------------------------------------------|
| ❌ Unused imports       | Imports not used anywhere in the file                   |
| 🔁 Duplicate imports    | Same import used more than once                         |
| ❌ Unused variables     | Assigned but never used local variables                 |
| 📝 TODO/FIXME/HACK      | Comments indicating unfinished or hacky code            |
| ⚠️ Long functions       | Functions longer than 50 lines (configurable)           |
| 🧱 Dead code            | Blocks of commented-out code detected as junk           |

---


# Sample output:
 Scanned 12 files
 Found 8 issues

[main.py]
 -  Unused import: os
 -  TODO at line 45
 -  Function 'start_server' is too long (64 lines)

💾 Report saved to cyrex_report.json
