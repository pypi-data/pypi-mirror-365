from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json
import os

console = Console()


def report_results(results, save_path="pyagentx_report.json"):
    """
    Display results in the terminal and save them as JSON.
    """
    total_files = len(results)
    total_issues = sum(len(r["issues"]) for r in results)

    console.print(f"\n[bold green] Scanned {total_files} files[/bold green]")
    console.print(f"[bold red]❗ Found {total_issues} issues[/bold red]\n")

    for result in results:
        file = result["file"]
        errors = result["errors"]
        issues = result["issues"]

        if errors:
            console.print(Panel(f"[red] {file}[/red]\n" + "\n".join(errors), title="Syntax Error", style="red"))
            continue

        if issues:
            table = Table(title=f"[cyan]{file}[/cyan]", show_lines=True)
            table.add_column("Type", style="bold yellow")
            table.add_column("Message", style="white")

            for issue in issues:
                table.add_row(issue["type"], issue["message"])

            console.print(table)

    # Save to JSON
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n [bold green]Report saved to:[/bold green] [underline]{save_path}[/underline]\n")
    except Exception as e:
        console.print(f"[red]Failed to write JSON report: {e}[/red]")


def save_json_report(data, path):
    """
    Save the report data to a JSON file.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def print_cli_report(report):
    """
    Print a simplified CLI report without Rich formatting for test purposes.
    """
    for file, issues in report.items():
        print(f"\nFile: {file}")
        for issue in issues:
            print(f" - [{issue['type']}] Line {issue.get('line', '?')}: {issue['details']}")
