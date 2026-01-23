#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path
from yt_dlp import YoutubeDL

from .formats import choose_formats
from .ytdlp_opts import build_base_opts, build_opts_for_format, cookie_sources


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


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


def run_download(url: str, ydl_opts: dict) -> bool:
    cf = ydl_opts.get("cookiefile")
    cb = ydl_opts.get("cookiesfrombrowser")
    print(f"[dbg] cookiefile={cf!r} cookiesfrombrowser={cb!r}")
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.download([url]) == 0


def build_cookie_attempts(base_with_cookies: dict) -> list[tuple[str, dict]]:
    attempts: list[tuple[str, dict]] = []

    if "cookiefile" in base_with_cookies:
        attempts.append(("cookiefile", dict(base_with_cookies)))
        return attempts

    for src in cookie_sources():
        o = dict(base_with_cookies)
        o["cookiesfrombrowser"] = src
        attempts.append((f"browser:{src[0]}", o))

    return attempts


def main() -> None:
    print("=== Universal video downloader (YouTube / X / Instagram / TikTok / Facebook) ===")
    print("Empty URL -> exit.\n")

    while True:
        url = ask("→ Paste URL: ")
        if not url:
            print("Done. Bye!")
            return

        target = ask("→ Output subfolder (relative to Downloads, empty = Downloads): ")

        try:
            out_dir = resolve_output_dir(target)
        except ValueError as e:
            print(f"❌ {e}")
            continue

        print(f"[i] Saving to: {out_dir}")

        exports = choose_formats(ask)
        print(f"[i] Export(s): {', '.join(exports)}")

        any_fail = False
        chosen_cookie_mode: str | None = None
        chosen_cookie_base: dict | None = None

        for export_ext in exports:
            print(f"\n=== Export: {export_ext} ===")

            base_no = build_base_opts(out_dir, enable_cookies=False)
            ydl_no = build_opts_for_format(base_no, export_ext)

            try:
                if run_download(url, ydl_no):
                    print(f"[i] Cookies: none")
                    print(f"✅ Done: {export_ext}")
                    continue
            except Exception:
                pass

            if chosen_cookie_base is not None:
                ydl_yes = build_opts_for_format(chosen_cookie_base, export_ext)
                try:
                    if run_download(url, ydl_yes):
                        print(f"✅ Done ({chosen_cookie_mode}): {export_ext}")
                        continue
                except Exception as e:
                    any_fail = True
                    print(f"❌ Error on export {export_ext} ({chosen_cookie_mode}): {e}")
                    continue

            base_yes = build_base_opts(out_dir, enable_cookies=True)
            attempts = build_cookie_attempts(base_yes)

            success = False
            last_err: str | None = None

            for mode, cookie_base in attempts:
                ydl_try = build_opts_for_format(cookie_base, export_ext)
                try:
                    if run_download(url, ydl_try):
                        chosen_cookie_mode = mode
                        chosen_cookie_base = cookie_base
                        print(f"[i] Cookies mode locked: {mode}")
                        print(f"✅ Done ({mode}): {export_ext}")
                        success = True
                        break
                except Exception as e:
                    last_err = str(e)
                    continue

            if not success:
                any_fail = True
                if last_err:
                    print(f"❌ Failed: {export_ext}: {last_err}")
                else:
                    print(f"❌ Failed: {export_ext}")

        if any_fail:
            print("\n⚠️ Finished with some errors.\n")
        else:
            print("\n✅ All exports complete.\n")


if __name__ == "__main__":
    main()
