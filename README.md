OK. Smireno. **Jedan blok. Jedan README. Ništa sa strane.**
Ovo ispod je **JEDINA stvar koju trebaš**. Otvori `README.md`, **select all → paste → save**. Kraj.

---

````markdown
# downloader

Universal interactive **video & audio downloader** powered by **yt-dlp**.

Supports downloading from **YouTube, X (Twitter), Instagram, TikTok, Facebook** and other platforms — including playlists — with automatic format selection, merging, and audio extraction.

Designed as a **clean CLI tool**, focused on reliability and real-world yt-dlp edge cases.

---

## Features

- Interactive CLI (no long command-line flags)
- Multiple export formats in a single run:
  - MP4 (default)
  - MKV
  - MOV
  - MP3 (audio-only)
- Best available video + audio merge via **ffmpeg**
- Playlist support (when supported by the platform)
- Automatic cookie handling:
  - Uses `cookies.txt` if present
  - Falls back to Firefox browser cookies
- Hardened YouTube setup:
  - Avoids broken WEB client
  - Uses `tv`, `mweb`, `tv_embedded` clients
  - JS challenge solving via **EJS**
  - Optional PO token support for mweb formats
- Safe filenames and long-title trimming
- Resume support and retry logic

---

## Requirements

- **Python** 3.10+
- **ffmpeg**
- **yt-dlp**
- *(Optional)* **Node.js** — required only for some YouTube JS challenges (EJS)

---

## Installation (Arch Linux)

```bash
sudo pacman -S ffmpeg nodejs
````

Clone the repository and prepare the environment:

```bash
git clone https://github.com/Ekart13/downloader.git
cd downloader

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

Run the script:

```bash
python downloader.py
```

You will be prompted for:

1. Video or playlist URL
2. Output directory
3. Export format(s)

### Export format selection

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

1. If `cookies.txt` exists next to `downloader.py`, it is used.
2. Otherwise, cookies are read directly from **Firefox**.

This enables access to:

* Age-restricted content
* Login-required videos
* Region-locked content (where cookies allow)

**Never commit `cookies.txt`.**
It is intentionally ignored via `.gitignore`.

---

## YouTube Notes

Due to frequent YouTube changes:

* The standard WEB client may be broken or SABR-only
* JS challenges may be required
* Some mweb formats require a PO token

This script:

* Avoids the WEB client entirely
* Enables **EJS + Node.js**
* Allows optional PO token injection

### Optional PO Token

```bash
export YTDLP_PO_TOKEN="mweb.gvs+YOUR_TOKEN_HERE"
```

Only required for specific YouTube formats.

---

## Output Format

Downloaded files are saved as:

```
Title [VideoID].ext
```

* Safe filenames enabled
* Title length trimmed automatically
* No overwrites between different export formats

---

## Troubleshooting

* **ffmpeg not found** → install `ffmpeg`
* **Node errors** → ensure `node` is in PATH
* **403 / login errors** → provide cookies
* **Playlist item failures** → expected; script continues

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

