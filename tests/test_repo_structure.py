"""Basic checks that required project files are present."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "PROTOCOL.md",
    "CLAUDE.md",
    ".env.example",
    "environment.yml",
    "pyproject.toml",
    "data/MANIFEST.md",
]


def test_required_files_exist() -> None:
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).exists()]
    assert not missing, f"Missing required files: {missing}"
