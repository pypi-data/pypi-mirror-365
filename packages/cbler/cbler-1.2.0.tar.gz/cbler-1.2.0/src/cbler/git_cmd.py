import typer
import pathlib
import subprocess
import sys
import datetime

from cbler.git_commands import create_tag

import hashlib
import importlib.util

from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from cbler.utils import aliased_command

from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from textual import events

HAVE_TEXTUAL = True

_git_console = Console()

_AUTHOR_COLORS = [
    "cyan",
    "magenta",
    "green",
    "yellow",
    "blue",
    "red",
]


def _author_color(name: str) -> str:
    """Return a color from the palette deterministically based on the name."""
    h = int(hashlib.md5(name.encode("utf-8")).hexdigest(), 16)
    return _AUTHOR_COLORS[h % len(_AUTHOR_COLORS)]


git_app = typer.Typer(help="Git helpers")


def _branch(path: pathlib.Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip() or None
    except Exception:
        return None


def _branches(path: pathlib.Path) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "branch", "--list"],
            stderr=subprocess.DEVNULL,
        )
        return [
            l.strip().lstrip("* ").strip()
            for l in out.decode().splitlines()
            if l.strip()
        ]
    except Exception:
        return []


def _local_branches(path: pathlib.Path) -> list[str]:
    """Return a list of local branch names for the repo at *path*."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "branch", "--format=%(refname:short)"],
            stderr=subprocess.DEVNULL,
        )
        return [b.strip().lstrip("* ") for b in out.decode().splitlines() if b.strip()]
    except Exception:
        return []


def _textual_select(current: str, branches: list[str]) -> str | None:
    spec = importlib.util.find_spec("textual")
    if not spec:
        return None
    from textual.app import App, ComposeResult
    from textual.widgets import Header, Footer, ListView, ListItem, Static

    selected: Optional[str] = None

    class MergeApp(App[str]):
        def compose(self) -> ComposeResult:
            yield Header(show_clock=False)
            yield Static(f"Current branch: [b]{current}[/b]\n")
            lv = ListView(*[ListItem(Static(b)) for b in branches])
            yield lv
            yield Footer()

        def on_list_view_selected(self, event: ListView.Selected) -> None:  # type: ignore[override]
            nonlocal selected
            selected = branches[event.index]
            self.exit()

    MergeApp().run()
    return selected


@aliased_command(git_app, aliases=["lg"])
def log(
    directory: str = typer.Argument(".", help="Repo dir"),
    num: int = typer.Argument(10, help="Commits to show"),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                box=box.ROUNDED,
            )
        )
    cmd = [
        "git",
        "-C",
        str(path),
        "log",
        f"-n{num}",
        "--pretty=format:%C(auto)%h%Creset|%C(yellow)%d%Creset|%s|%C(dim)%cr%Creset|%an|%b",
        "--decorate=short",
        "--date=relative",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
        lines = [l for l in out.splitlines() if l.strip()]
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    tbl = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        padding=(0, 1),
    )
    tbl.add_column("Hash", style="cyan", no_wrap=True)
    tbl.add_column("Ref", style="yellow", no_wrap=True)
    tbl.add_column("Message", style="white")
    tbl.add_column("When", style="dim", no_wrap=True)
    tbl.add_column("Who", no_wrap=True)
    tbl.add_column("Body", style="white")
    for line in lines:
        parts = line.split("|", maxsplit=5)
        while len(parts) < 6:
            parts.append("")
        parts = [p.strip() for p in parts]
        author = parts[4]
        color = _author_color(author)
        parts[4] = f"[{color}]{author}[/{color}]"
        tbl.add_row(*parts)
    _git_console.print(tbl)


@aliased_command(git_app, aliases=["df"])
def diff(
    directory: str = typer.Argument(".", help="Repo dir"),
    staged: bool = typer.Option(False, "--staged", "-s", help="Show staged diff"),
    include_untracked: bool = typer.Option(
        True, "--untracked/--no-untracked", "-u", help="Include untracked files"
    ),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                title="Branch",
            )
        )
    cmd = ["git", "-C", str(path), "diff", "--name-status"]
    if staged:
        cmd.append("--cached")
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    tbl = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE_HEAVY,
        title="Git Diff Status",
    )
    tbl.add_column("Status", no_wrap=True)
    tbl.add_column("File", style="white")
    had = False
    for line in out.strip().splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, fn = parts
            color = {
                "M": "yellow",
                "A": "green",
                "D": "red",
                "R": "cyan",
                "C": "cyan",
            }.get(status, "magenta" if status == "U" else "white")
            tbl.add_row(f"[{color}]{status}[/{color}]", fn)
            had = True
    if include_untracked and not staged:
        try:
            u = subprocess.check_output(
                ["git", "-C", str(path), "ls-files", "--others", "--exclude-standard"],
                stderr=subprocess.DEVNULL,
            )
            for f in u.decode().splitlines():
                tbl.add_row("[magenta]U[/magenta]", f)
                had = True
        except subprocess.CalledProcessError:
            pass
    if not had:
        tbl.add_row("-", "[dim]No changes[/dim]")
    _git_console.print(tbl)


@aliased_command(git_app, aliases=["tr"])
def tree(
    directory: str = typer.Argument(".", help="Repo dir"),
    num: int = typer.Option(20, "--num", "-n", help="Number of commits"),
):
    path = pathlib.Path(directory).resolve()
    br = _branch(path)
    if br:
        _git_console.print(
            Panel(
                f"[bold green]On branch:[/bold green] [yellow]{br}[/yellow]",
                title="Branch",
            )
        )
    cmd = [
        "git",
        "-C",
        str(path),
        "log",
        "--graph",
        "--oneline",
        "--decorate",
        f"-n{num}",
        "--color=never",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Error: {e.output.decode('utf-8')}[/red]")
        return
    _git_console.print(
        Panel(
            f"[white]{out}[/white]",
            title=f"Git Graph (last {num} commits)",
            subtitle="[dim]Use --num/-n to change depth[/dim]",
            style="cyan",
        )
    )


class BranchApp(App):  # pragma: no cover - UI logic
    """Simple TUI for switching git branches."""

    BINDINGS = [("n", "create_branch", "new branch"), ("q", "quit", "quit")]

    def __init__(self, repo: pathlib.Path, current: str, branches: list[str]):
        super().__init__()
        self.repo = repo
        self.current = current
        self.branches = branches

    def compose(self) -> ComposeResult:
        yield Static(f"Current: [bold green]{self.current}", id="header")
        items = [ListItem(Label(b)) for b in self.branches]
        items.append(ListItem(Label("+ New Branch"), id="new"))
        self.list = ListView(*items, id="list")
        # highlight current branch
        if self.current in self.branches:
            self.list.index = self.branches.index(self.current)
        yield self.list

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            item = self.list.children[self.list.index]
            label = item.query_one(Label).renderable
            if str(label) == "+ New Branch":
                await self.action_create_branch()
            else:
                subprocess.run(
                    ["git", "-C", str(self.repo), "switch", str(label)],
                    check=False,
                )
                self.exit()

    def action_create_branch(self) -> None:
        name = Prompt.ask("Branch name")
        if name:
            subprocess.run(
                ["git", "-C", str(self.repo), "switch", "-c", name],
                check=False,
            )
        self.exit()


@git_app.command()
def branch(directory: str = typer.Argument(".", help="Repo dir")) -> None:
    """Interactively switch branches."""

    path = pathlib.Path(directory).resolve()
    current = _branch(path) or ""
    branches = _branches(path)

    # Non-interactive or textual missing: print table
    if not sys.stdout.isatty() or not HAVE_TEXTUAL:
        tbl = Table(title="Branches", box=box.SIMPLE)
        tbl.add_column(" ", no_wrap=True)
        tbl.add_column("Name")
        for br in branches:
            mark = "*" if br == current else ""
            tbl.add_row(mark, br)
        _git_console.print(tbl)
        return

    BranchApp(path, current, branches).run()


@aliased_command(git_app, aliases=["cs"])
def cheatsheet() -> None:
    """Print a short cheatsheet of common git commands."""

    cheats: list[tuple[str, str]] = [
        ("git status", "Show working tree status"),
        ("git add <file>", "Stage file(s) for commit"),
        ("git commit -m 'msg'", "Commit staged changes"),
        ("git switch <branch>", "Switch branches"),
        ("git log --oneline", "Short commit history"),
    ]
    tbl = Table(
        title="Git Cheatsheet", box=box.SIMPLE_HEAVY, header_style="bold magenta"
    )
    tbl.add_column("Command", style="green", no_wrap=True)
    tbl.add_column("Description", style="white")
    for cmd, desc in cheats:
        tbl.add_row(cmd, desc)
    _git_console.print(tbl)


@git_app.command()
def tag(
    name: str = typer.Argument(None, help="Tag name"),
    directory: str = typer.Argument(".", help="Repo dir"),
    push: bool = typer.Option(False, "--push", help="Push tag to origin"),
) -> None:
    """Create a git tag at HEAD."""
    path = pathlib.Path(directory).resolve()
    if not name:
        default = f"v{datetime.datetime.now():%Y%m%d}"
        name = typer.prompt("Tag name", default=default)
    try:
        create_tag(name, path, push)
    except RuntimeError as e:
        _git_console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
    msg = f"Created tag [green]{name}[/green]"
    if push:
        msg += " and pushed to origin"
    _git_console.print(msg)


@git_app.command()
def merge(directory: str = typer.Argument(".", help="Repo dir")) -> None:
    """Interactively merge another branch into the current one."""

    path = pathlib.Path(directory).resolve()
    current = _branch(path)
    if not current:
        _git_console.print("[red]Not a git repository.[/red]")
        raise typer.Exit(code=1)

    branches = [b for b in _local_branches(path) if b != current]
    if not branches:
        _git_console.print("[yellow]No other branches found.[/yellow]")
        return

    if not sys.stdin.isatty():
        _git_console.print("[yellow]Interactive merge requires a TTY.[/yellow]")
        return

    if not HAVE_TEXTUAL:
        _git_console.print(
            "[yellow]Textual not installed. Install it with `uv add textual`.[/yellow]"
        )
        return

    selected = _textual_select(current, branches)

    if not selected:
        _git_console.print("[red]Merge cancelled.[/red]")
        return

    try:
        subprocess.check_call(["git", "-C", str(path), "merge", selected])
        _git_console.print("[green]Merge completed. Remember to git push.[/green]")
    except subprocess.CalledProcessError as e:
        _git_console.print(f"[red]Merge failed: {e}[/red]")
