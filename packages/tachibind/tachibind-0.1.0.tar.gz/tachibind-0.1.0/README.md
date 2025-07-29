# Manga Chapter → PDF (CLI)

Fetch chapter images from supported sites and export **one PDF per chapter**.  
Per-title folders, restart points, and batch limits.

## Features
- Per-chapter PDFs: `Title_ch123.pdf`
- Output under `downloads/<Title_Slug>/`
- Restart chapter via `mangas.json` (`start_at`)
- Mangapill adapter (extensible), simple scraper pipeline
- Batch mode with chapter limit and optional image cleanup

## Quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or: pip install requests beautifulsoup4 Pillow

# Edit mangas.json (title → url, selectors, start_at)
python quick_dl.py 'Berserk' 3  # grab 3 chapters from your restart
```
```
