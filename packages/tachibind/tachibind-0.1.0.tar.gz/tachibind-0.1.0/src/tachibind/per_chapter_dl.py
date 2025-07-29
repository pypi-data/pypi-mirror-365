#!/usr/bin/env python3
"""
Download every manga in mangas.json, chapter-by-chapter, and save one PDF per chapter
into a per-manga folder.

Usage examples:
  python per_chapter_dl.py --all                   # run for all titles
  python per_chapter_dl.py --titles "Berserk,Komi-san wa, Comyushou desu."
  python per_chapter_dl.py --all --limit 2         # smoke test (2 chapters per title)
  python per_chapter_dl.py --all --clean-images    # delete per-chapter images after PDF

Requires: requests, beautifulsoup4, Pillow
"""

import argparse, json, os, re, shutil, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# ---------------------- utilities ----------------------
def safe_name(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s).strip("_")

def chapter_num_from_href(href: str):
    m = re.search(r"(?:chapter[-/])(\d+(?:\.\d+)?)", href, re.I)
    return float(m.group(1)) if m else None

def http_get(url: str, timeout=20):
    r = requests.get(url, timeout=timeout, headers={"User-Agent": UA}, allow_redirects=True)
    r.raise_for_status()
    return r.text, r.url

def snapshot_url(url: str) -> str:
    p = urlparse(url)
    return f"https://r.jina.ai/http://{p.netloc}{p.path}"

def extract_chapter_links_from_html(html: str, base_url: str):
    soup = BeautifulSoup(html, "html.parser")
    hrefs = set()

    # Known list containers across popular mirrors
    selectors = [
        "li.a-h a",                 # Manganato / Chapmanganato
        "a.chapter-name",           # Many Kakalot mirrors
        ".chapter-list a",
        ".chapters__list a",
        "a[href^='/chapters/']",    # Mangapill
    ]
    for sel in selectors:
        for a in soup.select(sel):
            href = (a.get("href") or "").split("#")[0]
            if href:
                hrefs.add(urljoin(base_url, href))

    if not hrefs:
        # Fallback: any anchor that looks like a chapter URL
        for a in soup.find_all("a", href=True):
            h = a["href"].split("#")[0]
            if any(p in h for p in ("/chapter-", "/chapter/", "/chapters/", "/chap/")):
                hrefs.add(urljoin(base_url, h))

    items = []
    for h in hrefs:
        num = chapter_num_from_href(h)
        if num is None:
            # Some sites (e.g., Mangapill) embed number in link text
            a = soup.find("a", href=lambda x: x and h.endswith(x.split("#")[0]) if isinstance(x, str) else False)
            text = a.get_text(" ", strip=True) if a else ""
            m = re.search(r"(?:ch(?:apter)?\.?\s*)(\d+(?:\.\d+)?)", text, re.I)
            if m:
                try:
                    num = float(m.group(1))
                except ValueError:
                    num = None
        if num is not None:
            items.append((h, num))

    # sort ascending by chapter number (oldest first)
    items.sort(key=lambda kv: kv[1])
    return items

def extract_chapter_links(series_url: str):
    # 1) direct
    try:
        html, final_url = http_get(series_url, timeout=12)
        items = extract_chapter_links_from_html(html, final_url)
        if items:
            return items
    except Exception:
        final_url = series_url

    # 2) snapshot fallback (bypasses JS/CF in many cases)
    try:
        html, _ = http_get(snapshot_url(final_url), timeout=12)
        items = extract_chapter_links_from_html(html, final_url)
        if items:
            return items
    except Exception:
        pass

    # 3) mirror domain swaps
    host = urlparse(final_url).netloc
    candidates = []
    if "mangakakalot" in host:
        candidates = [
            final_url.replace(host, "chapmanganato.com"),
            final_url.replace(host, "manganato.com"),
            final_url.replace(host, "mangakakalot.gg"),
        ]
    elif "manganato" in host:
        candidates = [
            final_url.replace(host, "mangakakalot.to"),
            final_url.replace(host, "mangakakalot.gg"),
        ]

    for alt in candidates:
        try:
            html, alt_final = http_get(alt, timeout=12)
            items = extract_chapter_links_from_html(html, alt_final)
            if items:
                return items
            html, _ = http_get(snapshot_url(alt_final), timeout=12)
            items = extract_chapter_links_from_html(html, alt_final)
            if items:
                return items
        except Exception:
            continue
    return []

IMG_URL_RE = re.compile(r"https?://[^\s\"'>]+?\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"'>]*)?", re.I)

def extract_image_urls(chapter_url: str):
    # Try direct HTML first, then snapshot
    for attempt in ("direct", "snapshot"):
        try:
            html, final_url = (http_get(chapter_url, timeout=15) if attempt == "direct"
                               else http_get(snapshot_url(chapter_url), timeout=15))
            soup = BeautifulSoup(html, "html.parser")
            container = soup.select_one(".container-chapter-reader") or soup

            urls = []
            for img in container.find_all("img"):
                cand = (img.get("data-src") or img.get("data-original")
                        or img.get("data-lazy-src") or img.get("src") or "")
                if not cand:
                    srcset = img.get("srcset")
                    if srcset:
                        parts = [p.strip().split(" ")[0] for p in srcset.split(",") if p.strip()]
                        if parts:
                            cand = parts[-1]
                if cand:
                    if cand.startswith("//"):
                        cand = "https:" + cand
                    urls.append(cand)

            if not urls:
                urls = IMG_URL_RE.findall(html)

            # normalize & dedupe
            seen, out = set(), []
            for u in urls:
                if u.startswith("/"):
                    u = urljoin(final_url, u)
                if u.startswith("http") and u not in seen:
                    out.append(u); seen.add(u)

            if out:
                return out
        except Exception:
            continue
    return []

def download_image(url: str, dest: Path, referer: str | None):
    headers = {"User-Agent": UA}
    if referer:
        headers["Referer"] = referer
    for _ in range(3):
        try:
            with requests.get(url, timeout=30, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in r.iter_content(1 << 14):
                        if chunk:
                            f.write(chunk)
            return True
        except Exception:
            time.sleep(0.7)
    return False

def images_to_pdf(img_paths, out_pdf: Path):
    pages = []
    for p in img_paths:
        im = Image.open(p).convert("RGB")
        pages.append(im)
    if not pages:
        return False
    first, rest = pages[0], pages[1:]
    first.save(out_pdf, save_all=True, append_images=rest)
    return True

# ---------------------- main work ----------------------
def per_title(title: str, entry: dict, limit: int | None, clean_images: bool):
    url = entry.get("url")
    if not url:
        print(f"  • {title}: skipped (no url)")
        return

    restart_ch = int(entry.get("start_at", 1))  # we treat this as chapter number
    print(f"\n[{title}] url={url}\n  restart from chapter ≥ {restart_ch}")

    chapters = extract_chapter_links(url)
    if not chapters:
        print("  ! no chapter links found (even after fallbacks)")
        return

    # Prefer EN if site exposes multiple languages; keep one URL per chapter
    by_ch = {}
    for href, cnum in chapters:
        lang = "en" if "/en/" in href else ("ja" if "/ja/" in href else "")
        if cnum < restart_ch:
            continue
        if cnum not in by_ch or lang == "en":
            by_ch[cnum] = href

    # Build work list
    todo = [(by_ch[c], c) for c in sorted(by_ch)]
    if limit:
        todo = todo[:limit]
    print(f"  → will fetch {len(todo)} chapter(s)")

    # Output structure
    base = Path("downloads") / safe_name(title)
    imgs_dir = base / "imgs"
    base.mkdir(parents=True, exist_ok=True)
    imgs_dir.mkdir(parents=True, exist_ok=True)

    for i, (chap_url, cnum) in enumerate(todo, 1):
        cname = f"ch{int(cnum) if float(cnum).is_integer() else str(cnum).replace('.', 'p')}"
        out_pdf = base / f"{safe_name(title)}_{cname}.pdf"
        if out_pdf.exists():
            print(f"  [{i}/{len(todo)}] {cname}: exists, skipping")
            continue

        print(f"  [{i}/{len(todo)}] {cname} → {chap_url}")
        img_urls = extract_image_urls(chap_url)
        if not img_urls:
            print("     (no images found)")
            continue

        # download images
        per_ch_imgs = []
        for j, u in enumerate(img_urls, 1):
            img_path = imgs_dir / f"{cname}_{j:03d}.jpg"
            if img_path.exists():
                per_ch_imgs.append(str(img_path))
                continue
            ok = download_image(u, img_path, referer=chap_url)
            if ok:
                per_ch_imgs.append(str(img_path))
            else:
                print(f"     failed: {u}")

        if not per_ch_imgs:
            print("     (no images saved)")
            continue

        ok = images_to_pdf(per_ch_imgs, out_pdf)
        if ok:
            print(f"     [ok] wrote {out_pdf}")
            if clean_images:
                for p in per_ch_imgs:
                    try: os.remove(p)
                    except Exception: pass
        else:
            print("     [fail] PDF build failed")

def main():
    ap = argparse.ArgumentParser(description="Chapter-by-chapter downloader (one PDF per chapter).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="Download for all titles in mangas.json")
    g.add_argument("--titles", type=str, help="Comma-separated list of titles to download")
    ap.add_argument("--limit", type=int, default=None, help="Limit chapters per title (for testing)")
    ap.add_argument("--clean-images", action="store_true", help="Delete images after building each PDF")
    ap.add_argument("--file", default="mangas.json", help="Path to mangas.json")
    args = ap.parse_args()

    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    titles = list(data.keys()) if args.all else [t.strip() for t in args.titles.split(",")]

    # Put a few you care about first by just sorting
    titles.sort(key=lambda s: s.lower())

    for t in titles:
        entry = data.get(t)
        if not isinstance(entry, dict):
            print(f"• {t}: invalid entry, skipping")
            continue
        per_title(t, entry, args.limit, args.clean_images)

if __name__ == "__main__":
    main()
