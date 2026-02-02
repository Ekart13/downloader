from __future__ import annotations
from .ytdlp_opts import cookie_sources


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
