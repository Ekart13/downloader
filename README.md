
---


# ripbox

Universal interactive **video & audio downloader** written in **Python**, powered by **yt-dlp**.

Downloads from **YouTube, X (Twitter), Instagram, TikTok, Facebook**, and many other supported sites — including playlists — with automatic format selection, merging, and audio extraction.

Designed as a **clean Python CLI tool** focused on reliability and real-world yt-dlp behavior (not marketing promises).

---

## Core Features

- Interactive CLI (no long command-line flags)
- **Bulk downloads via `links.txt` (primary workflow)**
- Multiple export formats in a single run:
  - **MP4** (default)
  - **MKV**
  - **MOV** (best-effort)
  - **MP3** (audio-only)
- Best available **video + audio** merge via **ffmpeg**
- Playlist support (**soft mode by default**)
- Predictable output location:
  - Always uses the system **Downloads** directory
  - Optional subfolders are created automatically
- Automatic cookie handling:
  - Uses `cookies.txt` if present
  - Falls back to browser cookies (Firefox, Chromium-based)
- Hardened YouTube setup:
  - Avoids the broken WEB client
  - Uses `tv`, `mweb`, `tv_embedded` clients
  - JS challenge solving via **EJS** (Node.js)
  - Optional PO token support for some mweb formats
- Safe filenames + long-title trimming
- Resume support + retry logic
- Single-line download progress (no spam output)
- Clean exit handling (Ctrl+C at any time)

---

## Bulk Downloads (links.txt)

**`links.txt` is a first-class feature and the recommended way to use ripbox.**

### How it works

- Create a file named **`links.txt`** in the project root
- Add **one URL per line**
- Start `ripbox`
- When prompted for input, **press Enter on an empty line**

ripbox will automatically read and process all URLs from `links.txt`.

### Example `links.txt`



[https://www.youtube.com/watch?v=VIDEO_ID_1](https://www.youtube.com/watch?v=VIDEO_ID_1)
[https://www.youtube.com/watch?v=VIDEO_ID_2](https://www.youtube.com/watch?v=VIDEO_ID_2)
[https://www.instagram.com/reel/XXXXXXXX/](https://www.instagram.com/reel/XXXXXXXX/)
[https://x.com/user/status/XXXXXXXX](https://x.com/user/status/XXXXXXXX)

````

### Why this matters

- Ideal for **large batches**
- Easy to **edit, reuse, and version**
- Avoids pasting long URL lists into the terminal
- Automatically skips lines that are not valid links
- Makes ripbox suitable for scripted or repeatable workflows

If `links.txt` is missing, ripbox will notify you.

---

## Playlist Behavior

ripbox uses a **soft playlist mode** by default:

- If a playlist item is unavailable, private, or deleted:
  - It is skipped
  - The rest of the playlist continues downloading
- A playlist may complete with skipped entries without failing the entire run

This avoids unnecessary interruptions caused by broken or removed videos.

---

## Important Notes About Formats

Not all platforms provide all formats equally.

- **MP4** is the most reliable format across services
- **MKV** usually works where MP4 works
- **MOV** is best-effort:
  - Some platforms (especially YouTube) do not provide MOV-friendly streams
  - MOV export may fail due to container or ffmpeg limitations
- **MP3** works reliably as audio-only extraction

If a format fails for a specific platform, it’s often a **source/container limitation**, not a bug in ripbox.

---

## Requirements

- **Python** 3.10+
- **ffmpeg**
- **yt-dlp**
- *(Optional)* **Node.js** — only needed for some YouTube JS challenges (EJS)

---

## Installation

### Arch Linux


sudo pacman -S ffmpeg nodejs


Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/Ekart13/ripbox.git
cd ripbox

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### Recommended (installed CLI inside venv)

```bash
pip install -e .
ripbox
```

### Direct run (without installing)

```bash
python -m ripbox.cli
```

### Typical workflow (recommended)

1. Put URLs into `links.txt`
2. Run `ripbox`
3. Press **Enter** at the input prompt
4. Select output folder and formats
5. Let it run

You can press **Ctrl+C at any time** to exit cleanly.

---

## Output Directory Behavior

* **Empty input** → uses `~/Downloads`
* `yt` → `~/Downloads/yt`
* `yt/music` → `~/Downloads/yt/music`

Subfolders are created automatically.

---

## Export Format Selection

```
1 = MP4 (default)
2 = MKV
3 = MOV
4 = MP3 (audio-only)
```

Examples:

* Press **Enter** → MP4
* Type `4` → MP3 only
* Type `1 4` → MP4 and MP3

Each format is processed independently to avoid conflicts.

---

## Cookies & Authentication

Cookie handling is automatic:

1. If `cookies.txt` exists next to the project, it is used.
2. Otherwise, cookies are read directly from supported browsers.

This enables access to:

* Age-restricted content
* Login-required videos
* Region-locked content (where cookies allow)

### Creating `cookies.txt` manually (optional)

**Method 1: Using yt-dlp (recommended)**

```bash
yt-dlp --cookies-from-browser firefox --cookies cookies.txt
```

**Method 2: Browser extension**

Use an extension such as **Get cookies.txt** (Firefox / Chromium).

Steps:

1. Log in to the website
2. Export cookies
3. Save as `cookies.txt`
4. Place it in the project root

> Never commit `cookies.txt`.
> It is intentionally ignored via `.gitignore`.

---

## YouTube Notes

YouTube changes frequently:

* The standard WEB client may be broken or SABR-only
* JS challenges may be required
* Some mweb formats require a PO token

ripbox:

* Avoids the WEB client
* Enables **EJS + Node.js** when available
* Supports optional PO token injection

### Optional PO Token

```bash
export YTDLP_PO_TOKEN="mweb.gvs+YOUR_TOKEN_HERE"
```

---

## Output Filename Format

```
Title [VideoID].ext
```

* Safe filenames enabled
* Title length trimmed automatically
* No overwrites between different export formats

---

## Code Structure

```
ripbox/
  __init__.py
  cli.py            # Main CLI entrypoint and control flow
  downloader.py     # yt-dlp wrapper, progress handling, output verification
  cookies.py        # Cookie source handling and fallback logic
  paths.py          # Output directory resolution
  formats.py        # Format menu and selection logic
  ytdlp_opts.py     # yt-dlp base configuration
  url_checks.py     # Fast URL validation and error classification
```

---

## Security

* No telemetry
* No background services
* No credentials stored
* Cookies are read locally only

Transparent and auditable by design.

---

## License

MIT License

---

## Author

**Galeb**
GitHub: [https://github.com/Ekart13](https://github.com/Ekart13)

```

---

