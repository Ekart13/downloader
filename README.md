# downloader

Universal video downloader powered by yt-dlp.

## Requirements
- Python 3.10+
- ffmpeg
- yt-dlp
- (optional) node for YouTube JS challenges (EJS)

## Install (Arch Linux)
sudo pacman -S ffmpeg nodejs
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Run
python downloader.py

## Notes
- If `cookies.txt` exists next to the script, it will be used.
- Otherwise Firefox cookies are used automatically.
- Optional environment variable:
  - `YTDLP_PO_TOKEN` (for some YouTube mweb formats)
