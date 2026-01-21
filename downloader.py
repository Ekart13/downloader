#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal video downloader powered by yt-dlp.

What it does:
- Prompts for a URL and a target folder.
- Prompts for export format(s):
  - 1 = MP4 (default on Enter)
  - 2 = MKV
  - 3 = MOV
  - 4 = MP3 (audio-only)
  - You can type multiple like: 1 4  (downloads both mp4 and mp3)
- Creates the target folder if it doesn't exist.
- Downloads best available quality (best video + best audio when possible),
  then merges using ffmpeg.
- Works for single videos and playlists (when supported by the site).
- Uses cookies automatically:
  - If a `cookies.txt` file exists next to this script, it will use it.
  - Otherwise, it will read cookies from your Firefox profile.

YouTube notes (current reality):
- WEB client can be SABR-only / broken depending on rollout.
- JS challenge solving can be required -> we enable EJS + node runtime.
- mweb may require a PO token for some https formats (optional env var YTDLP_PO_TOKEN).
"""

from __future__ import annotations

from pathlib import Path
import shutil
from yt_dlp import YoutubeDL


# ----------------------------
# Helpers
# ----------------------------

def ask(prompt: str) -> str:
    """Read user input safely (handles Ctrl+C / Ctrl+D)."""
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def ensure_dir(path_str: str) -> Path:
    """Expand, resolve, and create the output directory."""
    out_dir = Path(path_str).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


# ----------------------------
# Format selection
# ----------------------------

FORMAT_MENU = {
    1: ("mp4", "Video MP4 (default)"),
    2: ("mkv", "Video MKV"),
    3: ("mov", "Video MOV"),
    4: ("mp3", "Audio MP3 (audio-only)"),
}


def choose_formats() -> list[str]:
    """
    Ask user which formats to export.
    - Enter => default mp4
    - multiple choices allowed: "1 4"
    Returns list like ["mp4", "mp3"] in the given order (deduped).
    """
    print("\nExport formats:")
    for k in sorted(FORMAT_MENU.keys()):
        ext, desc = FORMAT_MENU[k]
        default_tag = " (default)" if k == 1 else ""
        print(f"  {k}) {desc}{default_tag}")

    raw = ask("→ Choose format(s) by number (e.g. 1 4). Enter = default MP4: ")
    if not raw:
        return ["mp4"]

    picked: list[str] = []
    for token in raw.replace(",", " ").split():
        try:
            n = int(token)
        except ValueError:
            continue
        if n in FORMAT_MENU:
            ext = FORMAT_MENU[n][0]
            if ext not in picked:
                picked.append(ext)

    # If user typed only garbage -> fallback to default
    return picked if picked else ["mp4"]


# ----------------------------
# yt-dlp options
# ----------------------------

def build_base_opts(out_dir: Path) -> dict:
    """
    Build BASE yt-dlp options (shared for all formats).
    Then per-format tweaks are added in build_opts_for_format().
    """
    import os

    cookie_path = Path(__file__).with_name("cookies.txt")

    # Optional PO token for mweb (if you ever set it)
    # export YTDLP_PO_TOKEN="mweb.gvs+PASTE_TOKEN_HERE"
    po_token = os.environ.get("YTDLP_PO_TOKEN", "").strip()

    # Prefer non-web clients due to current WEB/SABR mess
    extractor_args = {
        "youtube": {
            "player_client": ["tv", "mweb", "tv_embedded"],
        }
    }
    if po_token:
        extractor_args["youtube"]["po_token"] = [po_token]

    opts = {
        # We'll override "format" / postprocessors per chosen export.
        "format": "bv*+ba/b",

        # Default container (overridden for mkv/mov)
        "merge_output_format": "mp4",

        # Output template (we append ".<export>" ourselves to avoid clashes)
        "outtmpl": str(out_dir / "%(title)s [%(id)s].%(ext)s"),

        # Reliability
        "noprogress": False,
        "ignoreerrors": True,
        "continuedl": True,
        "concurrent_fragment_downloads": 4,
        "retries": 10,
        "fragment_retries": 10,
        "nopart": False,

        # Headers / filenames
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "restrictfilenames": True,
        "trim_file_name": 200,

        # YouTube client selection + optional PO token
        "extractor_args": extractor_args,

        # EJS (JS challenge solver)
        "remote_components": ["ejs:github"],
    }

    # If node is available, tell yt-dlp explicitly (portable)
    node_path = shutil.which("node")
    if node_path:
        opts["js_runtimes"] = {"node": {"path": node_path}}


    # Cookies strategy
    if cookie_path.exists():
        opts["cookiefile"] = str(cookie_path)
    else:
        opts["cookiesfrombrowser"] = ("firefox",)

    return opts


def build_opts_for_format(base_opts: dict, export_ext: str) -> dict:
    """
    Return a COPY of base_opts customized for the requested export_ext.
    We run yt-dlp once per export format (most stable, avoids conflicts).
    """
    opts = dict(base_opts)  # shallow copy is enough (we'll replace nested keys we touch)

    # Make sure different exports don't overwrite each other:
    # For video exports, final ext comes from merge_output_format.
    # For mp3, final ext comes from postprocessor.
    if export_ext in ("mp4", "mkv", "mov"):
        opts["merge_output_format"] = export_ext
        opts["format"] = "bv*+ba/b"
        # Force filename extension to be the container we asked for
        opts["outtmpl"] = opts["outtmpl"].replace("%(ext)s", export_ext)

        # No special postprocessing required beyond merge (ffmpeg does it)
        opts.pop("postprocessors", None)

    elif export_ext == "mp3":
        # Audio-only best available, then transcode to mp3
        opts["format"] = "bestaudio/best"
        opts.pop("merge_output_format", None)

        # Ensure output ends with .mp3
        opts["outtmpl"] = opts["outtmpl"].replace("%(ext)s", "mp3")

        # Extract audio via ffmpeg
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # best VBR
            }
        ]

    else:
        # Unknown -> fallback to mp4
        opts["merge_output_format"] = "mp4"
        opts["format"] = "bv*+ba/b"
        opts["outtmpl"] = opts["outtmpl"].replace("%(ext)s", "mp4")
        opts.pop("postprocessors", None)

    return opts


# ----------------------------
# Main
# ----------------------------

def main() -> None:
    print("=== Universal video downloader (YouTube / X / Instagram / TikTok / Facebook) ===")
    print("Empty URL -> exit.\n")

    while True:
        url = ask("→ Paste URL: ")
        if not url:
            print("Done. Bye!")
            return

        target = ask("→ Output folder name or path (e.g. ~/Videos/Downloads): ")
        if not target:
            print("No folder provided. Try again.\n")
            continue

        out_dir = ensure_dir(target)
        print(f"[i] Saving to: {out_dir}")

        exports = choose_formats()
        print(f"[i] Export(s): {', '.join(exports)}")

        base_opts = build_base_opts(out_dir)

        any_fail = False
        for export_ext in exports:
            print(f"\n=== Export: {export_ext} ===")
            ydl_opts = build_opts_for_format(base_opts, export_ext)

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    result = ydl.download([url])  # 0 on success
                    if result == 0:
                        print(f"✅ Done: {export_ext}")
                    else:
                        any_fail = True
                        print(f"⚠️ Some items failed for export {export_ext}. Check logs above.")
            except Exception as e:
                any_fail = True
                print(f"❌ Error on export {export_ext}: {e}")

        if any_fail:
            print("\n⚠️ Finished with some errors.\n")
        else:
            print("\n✅ All exports complete.\n")


if __name__ == "__main__":
    main()
