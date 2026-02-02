from __future__ import annotations

from pathlib import Path

from .input_sources import choose_input
from .formats import choose_formats
from .paths import resolve_output_dir
from .cookies import build_cookie_attempts
from .downloader import run_download
from .ytdlp_opts import build_base_opts, build_opts_for_format
from .url_checks import (
    quick_url_check,
    is_networkish_error,
    is_permanent_unavailable_error,
)


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""
    except KeyboardInterrupt:
        # NIKAD ne gutaj Ctrl+C
        raise


def main() -> None:
    try:
        print("=== Universal video downloader (YouTube / X / Instagram / TikTok / Facebook) ===")
        print("Empty input -> exit.\n")

        last_out_dir: Path | None = None
        last_exports: list[str] | None = None

        while True:
            inp = choose_input(ask)

            if getattr(inp, "reset", False):
                last_out_dir = None
                last_exports = None
                print("[i] Reset done. Next run will ask for folder and format again.\n")
                continue

            if inp.source == "file" and not inp.text:
                print("❌ links.txt not found in project root.")
                continue

            if not inp.text:
                print("Done. Bye!")
                return

            if not inp.urls:
                print("❌ No URLs found in input.")
                continue

            urls = inp.urls
            total = len(urls)
            print(f"[i] Found {total} URL(s).")

            # ----------------------------
            # Output dir (sticky)
            # ----------------------------
            if last_out_dir is None:
                target = ask("→ Output subfolder (relative to Downloads, empty = Downloads): ")
                last_out_dir = resolve_output_dir(target)
                print(f"[i] Saving to: {last_out_dir}")
            else:
                print(f"[i] Using previous folder: {last_out_dir}")

            # ----------------------------
            # Export formats (sticky)
            # ----------------------------
            if last_exports is None:
                last_exports = choose_formats(ask)
                print(f"[i] Export(s): {', '.join(last_exports)}")
            else:
                print(f"[i] Using previous export(s): {', '.join(last_exports)}")

            out_dir = last_out_dir
            exports = last_exports

            chosen_cookie_mode: str | None = None
            chosen_cookie_base: dict | None = None

            ok_urls: list[str] = []
            fail_urls: list[str] = []
            invalid_urls: list[tuple[str, str]] = []

            # ----------------------------
            # Bulk loop
            # ----------------------------
            for idx, url in enumerate(urls, start=1):
                print(f"\n=== [{idx}/{total}] URL ===\n{url}")

                ok_url, why = quick_url_check(url)
                if not ok_url:
                    print(f"❌ Invalid/unreachable URL (fast check): {why}")
                    invalid_urls.append((url, why))
                    continue

                url_failed = False

                for export_ext in exports:
                    print(f"\n--- Export: {export_ext} ---")

                    # 1) no cookies
                    base_no = build_base_opts(out_dir, enable_cookies=False)
                    ydl_no = build_opts_for_format(base_no, export_ext)
                    r0 = run_download(url, ydl_no)

                    if r0.error == "Cancelled by user":
                        raise KeyboardInterrupt

                    if r0.ok:
                        print("[i] Cookies: none")
                        print(f"✅ Done: {export_ext}")
                        continue

                    if is_permanent_unavailable_error(r0.error):
                        url_failed = True
                        print(f"❌ Failed: {export_ext}: {r0.error}")
                        print("[i] Link/content appears unavailable — skipping cookie attempts.")
                        continue

                    if is_networkish_error(r0.error):
                        url_failed = True
                        print(f"❌ Failed: {export_ext}: {r0.error}")
                        print("[i] Looks like a network/SSL/DNS issue — skipping cookie attempts.")
                        continue

                    # 2) locked cookie mode
                    if chosen_cookie_base is not None:
                        ydl_locked = build_opts_for_format(chosen_cookie_base, export_ext)
                        r1 = run_download(url, ydl_locked)

                        if r1.error == "Cancelled by user":
                            raise KeyboardInterrupt

                        if r1.ok:
                            print(f"✅ Done ({chosen_cookie_mode}): {export_ext}")
                            continue

                        if is_permanent_unavailable_error(r1.error) or is_networkish_error(r1.error):
                            url_failed = True
                            print(f"❌ Failed: {export_ext}: {r1.error}")
                            print("[i] Skipping further cookie attempts.")
                            continue

                    # 3) try cookie sources
                    base_yes = build_base_opts(out_dir, enable_cookies=True)
                    attempts = build_cookie_attempts(base_yes)

                    last_err = r0.error
                    success = False

                    for mode, cookie_base in attempts:
                        ydl_try = build_opts_for_format(cookie_base, export_ext)
                        r2 = run_download(url, ydl_try)

                        if r2.error == "Cancelled by user":
                            raise KeyboardInterrupt

                        if r2.ok:
                            chosen_cookie_mode = mode
                            chosen_cookie_base = cookie_base
                            print(f"[i] Cookies mode locked: {mode}")
                            print(f"✅ Done ({mode}): {export_ext}")
                            success = True
                            break

                        last_err = r2.error
                        if is_permanent_unavailable_error(r2.error) or is_networkish_error(r2.error):
                            break

                    if not success:
                        url_failed = True
                        print(f"❌ Failed: {export_ext}: {last_err or 'unknown error'}")

                (fail_urls if url_failed else ok_urls).append(url)

            # ----------------------------
            # Summary
            # ----------------------------
            print("\n=== Summary ===")
            print(f"✅ OK: {len(ok_urls)}/{total}")
            print(f"❌ Failed: {len(fail_urls)}/{total}")
            print(f"⚠️ Invalid: {len(invalid_urls)}/{total}")

            if invalid_urls:
                print("\nInvalid URLs:")
                for u, reason in invalid_urls:
                    print(f"- {u}\n  -> {reason}")

            if fail_urls:
                print("\nFailed URLs (copy/paste):")
                for u in fail_urls:
                    print(f"- {u}")

            print("\n✅ Batch complete.\n")

    except KeyboardInterrupt:
        print("\nCiao 👋")
        return
