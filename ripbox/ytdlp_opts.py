from pathlib import Path
import shutil
import os


def cookie_sources() -> list[tuple[str, ...]]:
    return [
        ("firefox",),
        ("chromium",),
        ("chrome",),
        ("brave",),
        ("edge",),
        ("opera",),
        ("vivaldi",),
    ]


def build_base_opts(out_dir: Path, enable_cookies: bool = False) -> dict:
    cookie_path = Path(__file__).with_name("cookies.txt")
    po_token = os.environ.get("YTDLP_PO_TOKEN", "").strip()

    extractor_args = {
        "youtube": {
            "player_client": ["tv", "mweb", "tv_embedded"],
        }
    }
    if po_token:
        extractor_args["youtube"]["po_token"] = [po_token]

    opts = {
        "format": "bv*+ba/b",
        "merge_output_format": "mp4",
        "outtmpl": str(out_dir / "%(title)s [%(id)s].%(ext)s"),
        "ignoreerrors": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 4,
        "nopart": False,
        "noprogress": False,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "restrictfilenames": True,
        "trim_file_name": 200,
        "extractor_args": extractor_args,
        "remote_components": ["ejs:github"],
    }

    node_path = shutil.which("node")
    if node_path:
        opts["js_runtimes"] = {"node": {"path": node_path}}

    if enable_cookies:
        if cookie_path.exists():
            opts["cookiefile"] = str(cookie_path)

    return opts


def build_opts_for_format(base_opts: dict, export_ext: str) -> dict:
    opts = dict(base_opts)

    if export_ext in ("mp4", "mkv", "mov"):
        opts["merge_output_format"] = export_ext
        opts["format"] = "bv*+ba/b"
        opts["outtmpl"] = opts["outtmpl"].replace("%(ext)s", export_ext)
        opts.pop("postprocessors", None)

    elif export_ext == "mp3":
        opts["format"] = "bestaudio/best"
        opts.pop("merge_output_format", None)
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "0"}
        ]

    else:
        opts["merge_output_format"] = "mp4"
        opts["format"] = "bv*+ba/b"
        opts["outtmpl"] = opts["outtmpl"].replace("%(ext)s", "mp4")
        opts.pop("postprocessors", None)

    return opts
