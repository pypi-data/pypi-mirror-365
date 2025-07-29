import argparse, json, sys
from pathlib import Path
from tachibind import per_chapter_dl as P  # your module we just moved

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="tachibind",
        description="Fetch manga chapters and export one PDF per chapter."
    )
    ap.add_argument("title", help="Title exactly as in mangas.json")
    ap.add_argument("count", type=int, nargs="?", default=1,
                    help="How many chapters to fetch starting at restart (default: 1)")
    ap.add_argument("--clean-images", action="store_true", help="Delete downloaded images after PDF save")
    ap.add_argument("--cfg", default="mangas.json", help="Path to mangas.json (default: mangas.json)")
    args = ap.parse_args(argv)

    cfg_path = Path(args.cfg)
    if not cfg_path.exists():
        ap.error(f"Config not found: {cfg_path}")

    cfg = json.load(cfg_path.open(encoding="utf-8"))
    if args.title not in cfg:
        ap.error(f"Title not found in {cfg_path}: {args.title}")

    entry = cfg[args.title]
    # Use your existing per-title function
    P.per_title(args.title, entry, limit=args.count, clean_images=args.clean_images)

if __name__ == "__main__":
    main()
