import typer
import pathlib
import pyperclip
from typing import Sequence
from cbler.utils import aliased_command

import os
from cbler import utils
from cbler.report import print_tree, print_summary

code_app = typer.Typer(help="Concatenate code for different languages")

# -------- Language handlers ---------


def extract_py(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_gml(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_yy(path: str) -> str:
    import re
    import pathlib

    try:
        data = open(path, "r", encoding="utf-8").read()
        matches = re.findall(r'"code"\s*:\s*"([^"]+)"', data)
        if matches:
            return "\n\n".join(
                f"// Extracted Script {i + 1}:\n{code}"
                for i, code in enumerate(matches)
            )
        return f"// Object: {pathlib.Path(path).stem} (No code found)"
    except Exception as e:
        return f"// ⚠️ Error reading {path}: {e}"


# Each language defines:
#   - script_exts (tuple[str])
#   - object_exts (tuple[str])
#   - script_extractor (Callable)
#   - object_extractor (Callable | None)
LANGS: dict[str, dict] = {
    "py": {
        "script_exts": (".py",),
        "object_exts": tuple(),
        "script_extractor": extract_py,
        "object_extractor": None,
        "skip_dirs": {"venv", ".venv", "__pycache__", ".git"},
    },
    "gml": {
        "script_exts": (".gml",),
        "object_exts": (".yy",),
        "script_extractor": extract_gml,
        "object_extractor": extract_yy,
        "skip_dirs": {".git"},
    },
}

# -------- Simple, explicit filters ---------


def run_concat(
    lang_cfg: dict,
    base_path: pathlib.Path,
    *,
    prefix: Sequence[str],
    not_prefix: Sequence[str],
    suffix: Sequence[str],
    not_suffix: Sequence[str],
    contains: Sequence[str],
    not_contains: Sequence[str],
    path_contains: Sequence[str],
    not_path_contains: Sequence[str],
    parent_any: Sequence[str],  # OR
    parent_all: Sequence[str],  # AND (all must match)
    regex: bool,
    git_diff: bool,
    git_staged: bool,
    dry_run: bool,
    to_file: str | None,
    max_files: int | None,
    ignore_file: str | None,
):
    copied, skipped, pieces = [], [], []

    changed = set()
    if git_diff or git_staged:
        repo = utils.git_repo_root(base_path)
        if repo:
            changed = utils.git_changed_files(repo, staged=git_staged)
            changed = {
                utils.rel_path(repo / c, base_path)
                for c in changed
                if (repo / c).is_relative_to(base_path)
            }

    script_exts = lang_cfg["script_exts"]
    object_exts = lang_cfg["object_exts"]
    sx = lang_cfg["script_extractor"]
    ox = lang_cfg["object_extractor"]
    skip_dirs = lang_cfg.get("skip_dirs", set())
    if ignore_file is None:
        ignore_file = ".cblerignore"
    ignore_patterns = utils.load_ignore_patterns(base_path, ignore_file)

    for root, dirs, files in os.walk(base_path):
        # prune
        dirs[:] = [
            d
            for d in dirs
            if d not in skip_dirs
            and not utils.ignored(
                utils.rel_path(pathlib.Path(root, d), base_path), ignore_patterns
            )
        ]
        for fname in files:
            full = pathlib.Path(root, fname)
            rel = utils.rel_path(full, base_path)
            parent = utils.parent_dir_name(rel)

            if utils.ignored(rel, ignore_patterns):
                skipped.append(rel)
                continue

            # git filter
            if (git_diff or git_staged) and rel not in changed:
                skipped.append(rel)
                continue

            # positive filters
            if prefix and not utils.match_any(prefix, fname, regex, "start"):
                skipped.append(rel)
                continue
            if suffix and not utils.match_any(suffix, fname, regex, "end"):
                skipped.append(rel)
                continue
            if contains and not utils.match_any(contains, fname, regex, "any"):
                skipped.append(rel)
                continue
            if path_contains and not utils.match_any(path_contains, rel, regex, "any"):
                skipped.append(rel)
                continue
            if parent_any and not utils.match_any(parent_any, parent, regex, "any"):
                skipped.append(rel)
                continue
            if parent_all and not all(
                utils.match_any([p], parent, regex, "any") for p in parent_all
            ):
                skipped.append(rel)
                continue

            # negative filters
            if not_prefix and utils.match_any(not_prefix, fname, regex, "start"):
                skipped.append(rel)
                continue
            if not_suffix and utils.match_any(not_suffix, fname, regex, "end"):
                skipped.append(rel)
                continue
            if not_contains and utils.match_any(not_contains, fname, regex, "any"):
                skipped.append(rel)
                continue
            if not_path_contains and utils.match_any(
                not_path_contains, rel, regex, "any"
            ):
                skipped.append(rel)
                continue


            # Decide extractor
            text = None
            if fname.endswith(script_exts):
                text = sx(str(full))
                header = f"// Script: {rel}"
            elif fname.endswith(object_exts) and ox:
                text = ox(str(full))
                header = f"// Object: {rel}"
            if text is not None:
                copied.append(rel)
                if max_files is not None and len(copied) > max_files:
                    typer.secho(
                        f"Error: more than {max_files} files matched. Aborting.",
                        err=True,
                        fg="red",
                    )
                    raise typer.Exit(1)
                pieces.append(f"{header}\n{text}")
            else:
                skipped.append(rel)

    final_text = "\n\n".join(pieces)
    if not dry_run:
        if to_file:
            pathlib.Path(to_file).write_text(final_text, encoding="utf-8")
        else:
            pyperclip.copy(final_text)
    print_tree(copied, base_path, "Copied files")
    print_summary(len(copied), len(skipped))


# -------- Typer command ---------


@aliased_command(code_app, name=None, aliases=["ct"])
def concat(
    lang: str = typer.Argument(..., help="Language key: py | gml | ..."),
    path: str = typer.Argument(".", help="Project root"),
    # Positive filters
    prefix: list[str] = typer.Option(None, "--prefix", help="Filename startswith any"),
    suffix: list[str] = typer.Option(None, "--suffix", help="Filename endswith any"),
    contains: list[str] = typer.Option(
        None, "--contains", "-c", help="Filename contains any"
    ),
    path_contains: list[str] = typer.Option(
        None, "--path-contains", help="Relative path contains any"
    ),
    parent_any: list[str] = typer.Option(
        None, "--parent-contains", help="Parent dir matches ANY"
    ),
    parent_all: list[str] = typer.Option(
        None, "--parent-contains-all", help="Parent dir must match ALL"
    ),
    # Negative filters
    not_prefix: list[str] = typer.Option(
        None, "--not-prefix", help="Exclude: startswith any"
    ),
    not_suffix: list[str] = typer.Option(
        None, "--not-suffix", help="Exclude: endswith any"
    ),
    not_contains: list[str] = typer.Option(
        None, "--not-contains", help="Exclude: filename contains any"
    ),
    not_path_contains: list[str] = typer.Option(
        None, "--not-path-contains", help="Exclude: rel path contains any"
    ),
    # Misc
    regex: bool = typer.Option(
        True, "--regex/--no-regex", help="Treat patterns as regex"
    ),
    git_diff: bool = typer.Option(
        False, "--git-diff", help="Only include unstaged changed files"
    ),
    git_staged: bool = typer.Option(
        False, "--git-staged", help="Only include staged changed files"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print matched files without copying"
    ),
    to_file: str | None = typer.Option(
        None, "--to-file", help="Write concatenated output to this file"
    ),
    max_files: int | None = typer.Option(
        None,
        "--max-files",
        help="Fail if more than N files would be concatenated",
    ),
    ignore_file: str | None = typer.Option(
        None,
        "--ignore-file",
        help="Ignore patterns file (default .cblerignore)",
    ),
):
    """Concatenate files with filters"""
    cfg = LANGS.get(lang)
    if not cfg:
        raise typer.BadParameter(
            f"Unknown language '{lang}'. Known: {', '.join(LANGS)}"
        )
    run_concat(
        cfg,
        pathlib.Path(path).resolve(),
        prefix=prefix or [],
        not_prefix=not_prefix or [],
        suffix=suffix or [],
        not_suffix=not_suffix or [],
        contains=contains or [],
        not_contains=not_contains or [],
        path_contains=path_contains or [],
        not_path_contains=not_path_contains or [],
        parent_any=parent_any or [],
        parent_all=parent_all or [],
        regex=regex,
        git_diff=git_diff,
        git_staged=git_staged,
        dry_run=dry_run,
        to_file=to_file,
        max_files=max_files,
        ignore_file=ignore_file,
    )
