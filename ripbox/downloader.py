from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


# ----------------------------
# Result type
# ----------------------------
@dataclass(frozen=True)
class DownloadResult:
    ok: bool
    error: Optional[str] = None


# ----------------------------
# yt-dlp logger capture
# ----------------------------
class CaptureLogger:
    def __init__(self) -> None:
        self.last_error: str | None = None

    def debug(self, msg: str) -> None:
        # Ako ovo printaš, yt-dlp zna spamati.
        # Pusti samo “bitne” redove, ostalo ignoriraj.
        if not msg:
            return

        # Ovi redovi su najčešće korisni (ffmpeg merge i sl.)
        keep_prefixes = (
            "[Merger]",
            "[ffmpeg]",
            "[ExtractAudio]",
            "[Fixup",
        )
        if msg.startswith(keep_prefixes):
            print(msg)

    def warning(self, msg: str) -> None:
        if msg:
            print(f"WARNING: {msg}")

    def error(self, msg: str) -> None:
        self.last_error = msg
        if msg:
            print(f"ERROR: {msg}")


# ----------------------------
# Output verification helpers
# ----------------------------
def _existing_path(p: str | None) -> str | None:
    if not p:
        return None
    try:
        pp = Path(p)
        return str(pp) if pp.exists() else None
    except Exception:
        return None


def _collect_candidate_outputs(info: dict, ydl: YoutubeDL) -> list[str]:
    """
    Try multiple known places where yt-dlp stores the final output path.
    We treat download as success ONLY if at least one candidate exists on disk.
    """
    candidates: list[str] = []

    candidates.append(info.get("_filename"))

    try:
        candidates.append(ydl.prepare_filename(info))
    except Exception:
        pass

    rd = info.get("requested_downloads")
    if isinstance(rd, list):
        for item in rd:
            if isinstance(item, dict):
                candidates.append(item.get("filepath"))
                candidates.append(item.get("filename"))

    entries = info.get("entries")
    if isinstance(entries, list):
        for e in entries[:5]:
            if isinstance(e, dict):
                candidates.append(e.get("_filename"))
                try:
                    candidates.append(ydl.prepare_filename(e))
                except Exception:
                    pass

    seen: set[str] = set()
    existing: list[str] = []
    for c in candidates:
        ec = _existing_path(c)
        if ec and ec not in seen:
            seen.add(ec)
            existing.append(ec)

    return existing


# ----------------------------
# Progress hook (single-line)
# ----------------------------
def progress_hook(d: dict) -> None:
    status = d.get("status")

    if status == "downloading":
        percent = (d.get("_percent_str") or "").strip()
        speed = (d.get("_speed_str") or "").strip()
        eta = (d.get("_eta_str") or "").strip()

        frag = d.get("fragment_index")
        frag_total = d.get("fragment_count")

        frag_info = ""
        if frag and frag_total:
            frag_info = f" (frag {frag}/{frag_total})"

        # \r = vrati se na početak linije (overwrite)
        line = f"\r[download] {percent} at {speed} ETA {eta}{frag_info}"
        print(line, end="", flush=True)

    elif status == "finished":
        # očisti liniju malo na kraju (spaces)
        print("\r[download] Finished downloading.                          ")


# ----------------------------
# yt-dlp wrapper (success + real error string)
# ----------------------------
def run_download(url: str, ydl_opts: dict, *, debug_cookies: bool = False) -> DownloadResult:
    if debug_cookies:
        print(
            f"[dbg] cookiefile={ydl_opts.get('cookiefile')!r} "
            f"cookiesfrombrowser={ydl_opts.get('cookiesfrombrowser')!r}"
        )

    logger = CaptureLogger()

    opts = dict(ydl_opts)
    opts["logger"] = logger

    # Single-line progress: ugasi yt-dlp default ispis
    opts["quiet"] = True
    opts["no_warnings"] = True

    # Naš progress hook
    opts["progress_hooks"] = [progress_hook]

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if not isinstance(info, dict):
                return DownloadResult(False, logger.last_error or "No info extracted (download did not complete).")

            existing = _collect_candidate_outputs(info, ydl)
            if existing:
                return DownloadResult(True, None)

            return DownloadResult(False, logger.last_error or "No output file was created (treating as failure).")
    
    except KeyboardInterrupt:
        # očisti progress liniju ako je aktivna
        print("\r", end="", flush=True)
        return DownloadResult(False, "Cancelled by user")

    except DownloadError as e:
        return DownloadResult(False, logger.last_error or str(e))
    except Exception as e:
        return DownloadResult(False, logger.last_error or str(e))
