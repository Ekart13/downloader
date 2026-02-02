from __future__ import annotations
from pathlib import Path


def resolve_output_dir(user_input: str) -> Path:
    base = Path.home() / "Downloads"
    if not user_input:
        out_dir = base
    else:
        sub = Path(user_input)
        if sub.is_absolute():
            raise ValueError("Absolute paths are not allowed. Use subfolders only.")
        out_dir = base / sub

    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
