from __future__ import annotations
import os
import pathlib
import re
import subprocess
import fnmatch
from typing import Iterable, Sequence, Callable, Any, Optional, Iterator
import typer

# -------- Git helpers ---------


def git_repo_root(path: pathlib.Path) -> pathlib.Path | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
        )
        return pathlib.Path(out.decode().strip())
    except Exception:
        return None


def git_changed_files(repo_root: pathlib.Path, staged: bool = False) -> set[str]:
    cmd = ["git", "-C", str(repo_root), "diff", "--name-only"]
    if staged:
        cmd.append("--cached")
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return {p.replace("\\", "/") for p in out.decode().splitlines() if p.strip()}
    except subprocess.CalledProcessError:
        return set()


# -------- Path helpers ---------


def rel_path(path: str | pathlib.Path, base: pathlib.Path) -> str:
    return os.path.relpath(path, base).replace("\\", "/")


def parent_dir_name(rel: str) -> str:
    return pathlib.Path(rel).parent.name


# -------- Ignore helpers ---------


def _read_ignore_file(base: pathlib.Path, name: str) -> list[str]:
    path = pathlib.Path(name)
    if not path.is_absolute():
        path = base / path
    if not path.exists():
        return []
    lines: list[str] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def _prep_pattern(pat: str) -> str:
    if pat.startswith("/"):
        return pat.lstrip("/")
    return pat


def load_ignore_patterns(base: pathlib.Path, *names: str) -> list[str]:
    patterns: list[str] = []
    for name in names:
        patterns.extend(_read_ignore_file(base, name))
    return [_prep_pattern(p) for p in patterns]


def ignored(rel: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in patterns)


def walk_files(base: pathlib.Path, patterns: Sequence[str]) -> Iterator[pathlib.Path]:
    for root, dirs, files in os.walk(base):
        rel_root = os.path.relpath(root, base)
        if rel_root == ".":
            rel_root = ""
        dirs[:] = [d for d in dirs if not ignored(os.path.join(rel_root, d), patterns)]
        for f in files:
            rel = os.path.join(rel_root, f)
            if ignored(rel, patterns):
                continue
            yield pathlib.Path(root, f)


def is_binary_file(path: pathlib.Path) -> bool:
    try:
        with open(path, "rb") as fh:
            chunk = fh.read(1024)
            if b"\0" in chunk:
                return True
            chunk.decode("utf-8")
    except Exception:
        return True
    return False

# -------- Matching helpers -----


def _ensure_iter(x: Sequence[str] | None) -> list[str]:
    return list(x or [])


def match_any(
    patterns: Iterable[str], value: str, regex: bool, mode: str = "any"
) -> bool:
    """Return True if *any* pattern matches value. modes: start|end|any."""
    for pat in patterns:
        if regex:
            try:
                if mode == "start" and re.match(pat, value):
                    return True
                if mode == "end" and re.search(f"{pat}$", value):
                    return True
                if mode == "any" and re.search(pat, value):
                    return True
            except re.error:
                continue
        else:
            if mode == "start" and value.startswith(pat):
                return True
            if mode == "end" and value.endswith(pat):
                return True
            if mode == "any" and pat in value:
                return True
    return False


# -------- Typer helpers ---------


def aliased_command(
    app: "typer.Typer",
    *,
    aliases: Optional[Iterable[str]] = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a command with optional aliases."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        app.command(**kwargs)(func)
        for alias in aliases or []:
            alias_kwargs = dict(kwargs)
            alias_kwargs["name"] = alias
            app.command(**alias_kwargs)(func)
        return func

    return decorator
