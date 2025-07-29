import subprocess
import pathlib


def create_tag(tag: str, repo: pathlib.Path, push: bool = False) -> None:
    """Create a git tag in *repo* and optionally push it."""
    # check for existing tag
    res = subprocess.run(
        ["git", "-C", str(repo), "tag", "-l", tag],
        capture_output=True,
        text=True,
    )
    if res.stdout.strip():
        raise RuntimeError(f"Tag '{tag}' already exists")

    subprocess.check_call(["git", "-C", str(repo), "tag", tag])
    if push:
        subprocess.check_call(["git", "-C", str(repo), "push", "origin", tag])
