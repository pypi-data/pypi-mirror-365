import pathlib
import re
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from cbler.code_cmd import code_app
from cbler.git_cmd import git_app
from cbler import utils

_console = Console()

app = typer.Typer(
    add_completion=False, no_args_is_help=True, help="cbler: concat & git helpers"
)
app.add_typer(code_app, name="code", help="Concatenate source files")
app.add_typer(code_app, name="c")  # alias

app.add_typer(git_app, name="git", help="Git utilities")
app.add_typer(git_app, name="g")  # alias


@app.command()
def stats(path: str = typer.Option(".", "--path", help="Project directory")) -> None:
    """Show code statistics grouped by extension."""
    base = pathlib.Path(path).resolve()
    patterns = utils.load_ignore_patterns(base, ".gitignore")
    patterns.append(".git")
    counts: dict[str, dict[str, int]] = {}
    for fp in utils.walk_files(base, patterns):
        ext = fp.suffix or ""
        try:
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        stat = counts.setdefault(ext, {"files": 0, "lines": 0, "blank": 0, "code": 0})
        stat["files"] += 1
        stat["lines"] += len(lines)
        blanks = sum(1 for l in lines if not l.strip())
        stat["blank"] += blanks
        stat["code"] += len(lines) - blanks
    tbl = Table(show_header=True, header_style="bold magenta")
    tbl.add_column("Ext", style="cyan")
    tbl.add_column("Files", justify="right")
    tbl.add_column("Lines", justify="right")
    tbl.add_column("Blank", justify="right")
    tbl.add_column("Code", justify="right")
    for ext, d in sorted(counts.items()):
        tbl.add_row(ext or "[none]", str(d["files"]), str(d["lines"]), str(d["blank"]), str(d["code"]))
    _console.print(tbl)


@app.command()
def todo(
    path: str = typer.Option(".", "--path", help="Project directory"),
    ext: list[str] = typer.Option(None, "--ext", help="Filter extensions"),
) -> None:
    """Find TODO/FIXME/NOTE comments."""
    base = pathlib.Path(path).resolve()
    patterns = utils.load_ignore_patterns(base, ".gitignore")
    regex = re.compile(r"(?i)(TODO|FIXME|NOTE)")
    tbl = Table(show_header=True, header_style="bold magenta")
    tbl.add_column("File", style="cyan")
    tbl.add_column("Line", justify="right")
    tbl.add_column("Comment")
    for fp in utils.walk_files(base, patterns):
        if ext and fp.suffix not in ext:
            continue
        if utils.is_binary_file(fp):
            continue
        try:
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        rel = utils.rel_path(fp, base)
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                tbl.add_row(rel, str(i), line.strip())
    if tbl.row_count:
        _console.print(tbl)
    else:
        _console.print("No TODOs found")


@app.command()
def explore(
    term: str,
    path: str = typer.Option(".", "--path", help="Project directory"),
    ext: list[str] = typer.Option(None, "--ext", help="Filter extensions"),
) -> None:
    """Search for an identifier across files."""
    base = pathlib.Path(path).resolve()
    patterns = utils.load_ignore_patterns(base, ".gitignore")
    found = False
    for fp in utils.walk_files(base, patterns):
        if ext and fp.suffix not in ext:
            continue
        if utils.is_binary_file(fp):
            continue
        try:
            lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for idx, line in enumerate(lines):
            if term in line:
                start = max(0, idx - 2)
                end = min(len(lines), idx + 3)
                snippet = "\n".join(lines[start:end])
                rel = utils.rel_path(fp, base)
                panel = Panel(snippet, title=f"{rel}:{idx+1}", expand=False)
                _console.print(panel)
                found = True
    if not found:
        _console.print("No matches found")

if __name__ == "__main__":  # pragma: no cover
    app()
