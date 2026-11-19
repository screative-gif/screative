#!/usr/bin/env python3
"""
Agent Riset Tren — Pengumpul Data (Threads, X, Instagram, TikTok) via Apify.

Cara pakai:
  python3 collect.py              # ambil data sungguhan (butuh APIFY_TOKEN di .env)
  python3 collect.py --dry-run    # tes pakai data contoh, tanpa token & tanpa biaya
  python3 collect.py --only tiktok,threads   # hanya platform tertentu

Hanya pakai library bawaan Python 3 (tidak perlu pip install).
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "https://api.apify.com/v2"


# ---------------------------------------------------------------- config & token
def load_config():
    with open(ROOT / "config.json", encoding="utf-8") as f:
        return json.load(f)


def load_token():
    token = os.environ.get("APIFY_TOKEN", "").strip()
    env_file = ROOT / ".env"
    if not token and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("APIFY_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
    return token


# ---------------------------------------------------------------- input per platform
def build_input(platform, cfg):
    kw = cfg["keywords"]
    tags = [t.lstrip("#") for t in cfg.get("hashtags", [])]
    n = cfg["platforms"][platform]["results_per_query"]

    if platform == "tiktok":  # clockworks/tiktok-scraper
        return {
            "searchQueries": kw,
            "hashtags": tags,
            "resultsPerPage": n,
            "searchSection": "/video",
        }
    if platform == "instagram":  # apify/instagram-hashtag-scraper
        # IG pakai hashtag; kalau kosong, keyword dipakai sebagai pencarian kata kunci
        return {
            "hashtags": tags or kw,
            "keywordSearch": not tags,
            "resultsType": "posts",
            "resultsLimit": n,
        }
    if platform == "ig_akun":  # apify/instagram-post-scraper: akun sendiri + akun referensi
        return {
            "username": cfg["platforms"]["ig_akun"].get("accounts", []),
            "resultsLimit": n,
            "dataDetailLevel": "basicData",
        }
    if platform == "x":  # xquik/x-tweet-scraper
        terms = kw + [f"#{t}" for t in tags]
        inp = {"searchTerms": terms, "maxItemsPerTarget": n, "maxItems": n * len(terms), "queryType": "Top"}
        if cfg.get("language"):
            inp["lang"] = "in" if cfg["language"] == "id" else cfg["language"]  # X pakai kode "in"
        if cfg.get("days_back"):
            inp["since"] = (dt.date.today() - dt.timedelta(days=cfg["days_back"])).isoformat()
        return inp
    if platform == "threads":  # scrapesage/threads-search-scraper
        return {
            "keywords": kw,
            "hashtags": tags,
            "maxPerSource": n,
            "maxResults": n * (len(kw) + len(tags)),
            "excludeReplies": True,
        }
    raise ValueError(platform)


# ---------------------------------------------------------------- panggil Apify
def run_actor(actor_id, run_input, token, max_usd, timeout_s=300):
    actor = actor_id.replace("/", "~")
    qs = urllib.parse.urlencode({"maxTotalChargeUsd": max_usd, "timeout": timeout_s})
    req = urllib.request.Request(
        f"{API}/acts/{actor}/run-sync-get-dataset-items?{qs}",
        data=json.dumps(run_input).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s + 30) as r:
        return json.loads(r.read().decode())


# ---------------------------------------------------------------- normalisasi
def pick(item, *paths, default=None):
    """Ambil field pertama yang ada. Path pakai titik: 'author.userName'."""
    for p in paths:
        cur = item
        for part in p.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if cur not in (None, ""):
            return cur
    return default


def num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def tags_of(item, text):
    raw = pick(item, "hashtags", "entities.hashtags", default=[]) or []
    out = []
    for t in raw:
        if isinstance(t, dict):
            t = t.get("name") or t.get("text") or t.get("tag")
        if t:
            out.append(str(t).lstrip("#").lower())
    if not out and text:
        out = [w.strip("#.,!?:;").lower() for w in str(text).split() if w.startswith("#") and len(w) > 1]
    return sorted(set(out))


def normalize(platform, item):
    text = pick(item, "text", "fullText", "caption", "content", "description", "post_text", default="")
    row = {
        "platform": platform,
        "query": pick(item, "searchQuery", "sourceQuery", "input", "searchTerm", "query", "keyword", "inputUrl", "source", default=""),
        "url": pick(item, "webVideoUrl", "url", "twitterUrl", "postUrl", "post_url", "link", default=""),
        "author": pick(item, "authorMeta.name", "ownerUsername", "author.userName", "author.username",
                       "user.username", "username", "author", default=""),
        "followers": num(pick(item, "authorMeta.fans", "author.followers", "user.follower_count",
                              "authorFollowers", "followers")),
        "created_at": pick(item, "createTimeISO", "timestamp", "createdAt", "created_at", "taken_at",
                           "publishedAt", "date", default=""),
        "likes": num(pick(item, "diggCount", "likesCount", "likeCount", "like_count", "likes", "stats.likes")),
        "comments": num(pick(item, "commentCount", "commentsCount", "replyCount", "reply_count",
                             "replies", "stats.replies")),
        "shares": num(pick(item, "shareCount", "sharesCount", "retweetCount", "repostCount", "repost_count", "reposts",
                           "stats.reposts")),
        "views": num(pick(item, "playCount", "videoPlayCount", "videoViewCount", "viewCount", "views")),
        "hashtags": "",
        "text": " ".join(str(text).split())[:1000],
    }
    if isinstance(row["author"], dict):
        row["author"] = row["author"].get("userName") or row["author"].get("username") or ""
    row["hashtags"] = " ".join(tags_of(item, text))
    row["engagement"] = row["likes"] + 2 * row["comments"] + 3 * row["shares"]
    row["format"] = detect_format(platform, item)
    row["age_days"] = age_days(row["created_at"])
    row["duration_s"] = num(pick(item, "videoMeta.duration", "videoDuration"))
    return row


def detect_format(platform, item):
    if platform == "tiktok":
        return "slideshow" if item.get("isSlideshow") else "video"
    if platform in ("instagram", "ig_akun"):
        t = str(item.get("type", "")).lower()
        return {"sidecar": "carousel", "video": "reels", "image": "foto"}.get(t, t or "?")
    if platform == "x":
        media = item.get("media") or (item.get("extendedEntities") or {}).get("media") or []
        kinds = {str(m.get("type", "")).lower() for m in media if isinstance(m, dict)}
        return "video" if kinds & {"video", "animated_gif"} else ("gambar" if media else "teks")
    if platform == "threads":
        if item.get("videoUrl"):
            return "video"
        return "gambar" if item.get("hasMedia") else "teks"
    return "?"


def age_days(created):
    """Umur post dalam hari (None kalau tanggal tidak terbaca)."""
    if not created:
        return None
    s = str(created)
    for fmt in ("%a %b %d %H:%M:%S %z %Y",):
        try:
            d = dt.datetime.strptime(s, fmt)
            break
        except ValueError:
            d = None
    if d is None:
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            try:
                d = dt.datetime.fromtimestamp(float(s), tz=dt.timezone.utc)
            except ValueError:
                return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return round((dt.datetime.now(dt.timezone.utc) - d).total_seconds() / 86400, 1)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="pakai data contoh di samples/")
    ap.add_argument("--only", default="", help="contoh: tiktok,threads")
    ap.add_argument("--limit", type=int, default=0, help="timpa results_per_query (untuk tes murah)")
    args = ap.parse_args()

    cfg = load_config()
    if args.limit:
        for v in cfg["platforms"].values():
            v["results_per_query"] = args.limit
    platforms = [p for p, v in cfg["platforms"].items() if v.get("enabled")]
    if args.only:
        platforms = [p for p in platforms if p in args.only.split(",")]

    token = "" if args.dry_run else load_token()
    if not args.dry_run and not token:
        sys.exit("APIFY_TOKEN belum diisi. Salin .env.example jadi .env lalu isi token-nya (lihat README.md).")

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    out_dir = ROOT / "data" / stamp
    (out_dir / "raw").mkdir(parents=True, exist_ok=True)

    rows, summary = [], []
    for p in platforms:
        pc = cfg["platforms"][p]
        run_input = build_input(p, cfg)
        print(f"→ {p:<9} actor={pc['actor']}  budget maks ${pc['max_usd_per_run']}")
        try:
            if args.dry_run:
                items = json.loads((ROOT / "samples" / f"{p}.json").read_text(encoding="utf-8"))
            else:
                items = run_actor(pc["actor"], run_input, token, pc["max_usd_per_run"])
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")[:300]
            print(f"   ✗ gagal (HTTP {e.code}): {body}")
            summary.append({"platform": p, "status": f"error {e.code}", "items": 0})
            continue
        except Exception as e:  # noqa: BLE001
            print(f"   ✗ gagal: {e}")
            summary.append({"platform": p, "status": "error", "items": 0})
            continue

        items = [i for i in items if isinstance(i, dict) and not i.get("error") and not i.get("noResults")]
        (out_dir / "raw" / f"{p}.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        norm = [normalize(p, i) for i in items]
        rows += norm
        print(f"   ✓ {len(norm)} post")
        summary.append({"platform": p, "status": "ok", "items": len(norm)})

    rows.sort(key=lambda r: r["engagement"], reverse=True)
    fields = ["platform", "query", "format", "engagement", "likes", "comments", "shares", "views",
              "author", "followers", "created_at", "age_days", "hashtags", "url", "text"]
    with open(out_dir / "posts.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (out_dir / "posts.json").write_text(json.dumps(
        {"collected_at": stamp, "niche": cfg.get("niche"), "keywords": cfg["keywords"],
         "hashtags": cfg.get("hashtags", []), "summary": summary, "posts": rows},
        ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nSelesai: {len(rows)} post → {out_dir.relative_to(ROOT)}/posts.csv (+ posts.json, raw/)")


if __name__ == "__main__":
    main()
