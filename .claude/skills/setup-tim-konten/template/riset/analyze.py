#!/usr/bin/env python3
"""
Agent Riset Tren: Analisis Statistik.

Membaca hasil collect.py terbaru, lalu menghitung:
  - post yang performanya jauh di atas rata-rata (outlier)
  - hashtag & frasa yang paling banyak membawa engagement
  - format konten terbaik per platform
  - contoh hook (kalimat pembuka) dari post teratas
  - perbandingan dengan pengambilan data sebelumnya (apa yang naik / baru)

Hasilnya: data/<run>/summary.md (dibaca Claude untuk laporan) dan summary.json.

  python3 analyze.py                  # run terbaru
  python3 analyze.py --run 2026-11-17_1444
"""
import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

import collect

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

STOP = set("""
yang dan di ke dari ini itu untuk dengan ada tidak aku kamu kita kami mereka dia saya gue gw lo lu
juga jadi bisa akan sudah udah lagi aja saja kalau kalo karena buat biar atau tapi pada dalam
nya ya yg ga gak nggak enggak banget sih dong kok deh nih tuh lah pun mau harus masih belum
sama lebih paling cuma hanya semua satu dua tiga apa siapa kenapa gimana bagaimana kapan mana
the a an of to in for on and or is are be it this that with you your i my we our at as by from
so if not do does can will just how what why when all more most out up about me
""".split())
GENERIC_TAGS = {"fyp", "fypシ", "foryou", "foryoupage", "viral", "xyzbca", "trending", "fy", "fypage",
                "explore", "explorepage", "reels", "reel", "tiktok", "instagram", "threads"}


def runs():
    return sorted(p for p in DATA.iterdir() if p.is_dir() and (p / "raw").exists()) if DATA.exists() else []


def load_rows(run_dir):
    rows, seen = [], set()
    for f in sorted((run_dir / "raw").glob("*.json")):
        platform = f.stem
        for item in json.loads(f.read_text(encoding="utf-8")):
            r = collect.normalize(platform, item)
            key = r["url"] or (platform, r["text"][:80])
            if key in seen:
                continue
            seen.add(key)
            rows.append(r)
    return rows


def words(text):
    text = re.sub(r"https?://\S+|[@#]\w+", " ", text.lower())
    return [w for w in re.findall(r"[a-zà-ÿ0-9]+", text) if len(w) > 2 and w not in STOP and not w.isdigit()]


def phrases(text):
    w = words(text)
    return {f"{a} {b}" for a, b in zip(w, w[1:])}


def hook(text):
    m = re.split(r"(?<=[.!?…])\s|\s[-–|]\s|[\n💸✅👉🔥]", text, maxsplit=1)
    h = m[0].strip()
    return h[:120] + ("…" if len(h) > 120 else "")


def weighted(rows, extractor, exclude=()):
    eng, cnt = Counter(), Counter()
    for r in rows:
        for k in extractor(r):
            if k and k not in exclude:
                eng[k] += r["engagement"]
                cnt[k] += 1
    return eng, cnt


def analyze(rows, cfg):
    days = cfg.get("days_back", 14)
    seeds = {t.lstrip("#").lower() for t in cfg.get("hashtags", [])}
    recent = [r for r in rows if r["age_days"] is not None and r["age_days"] <= days]
    old = [r for r in rows if r not in recent]

    by_p = defaultdict(list)
    for r in rows:
        by_p[r["platform"]].append(r)
    med = {p: statistics.median([r["engagement"] for r in rs]) for p, rs in by_p.items()}
    for r in rows:
        # lantai 20 supaya platform dengan banyak post 0-like (mis. X) tidak menghasilkan angka absurd
        r["outlier_x"] = round(r["engagement"] / max(med[r["platform"]], 20), 1)

    platforms = {}
    for p, rs in by_p.items():
        fmt = defaultdict(list)
        for r in rs:
            fmt[r["format"]].append(r["engagement"])
        p_tag_eng, p_tag_cnt = weighted(rs, lambda r: r["hashtags"].split(), GENERIC_TAGS | seeds)
        p_ph_eng, p_ph_cnt = weighted(rs, lambda r: phrases(r["text"]), {k.lower() for k in cfg["keywords"]})
        p_recent = sorted([r for r in rs if r in recent], key=lambda r: -r["outlier_x"])
        platforms[p] = {
            "top_hashtags": [{"tag": t, "posts": p_tag_cnt[t], "engagement": e}
                             for t, e in p_tag_eng.most_common(8)],
            "top_phrases": [{"phrase": k, "posts": p_ph_cnt[k], "engagement": e}
                            for k, e in p_ph_eng.most_common(40) if p_ph_cnt[k] >= 2][:8],
            "top_recent": [slim(r) for r in p_recent[:10]],
            "posts": len(rs),
            "recent_posts": sum(1 for r in rs if r in recent),
            "median_engagement": med[p],
            "formats": {f: {"posts": len(v), "median_engagement": statistics.median(v)}
                        for f, v in sorted(fmt.items(), key=lambda kv: -statistics.median(kv[1]))},
        }

    tag_eng, tag_cnt = weighted(rows, lambda r: r["hashtags"].split(), GENERIC_TAGS | seeds)
    ph_eng, ph_cnt = weighted(rows, lambda r: phrases(r["text"]),
                              {k.lower() for k in cfg["keywords"]})
    top = sorted(rows, key=lambda r: -r["outlier_x"])

    return {
        "days_back": days,
        "total_posts": len(rows),
        "recent_posts": len(recent),
        "old_posts": len(old),
        "platforms": platforms,
        "top_hashtags": [{"tag": t, "posts": tag_cnt[t], "engagement": e} for t, e in tag_eng.most_common(20)],
        "top_phrases": [{"phrase": k, "posts": ph_cnt[k], "engagement": e}
                        for k, e in ph_eng.most_common(60) if ph_cnt[k] >= 2][:20],
        "outliers_recent": [slim(r) for r in top if r in recent][:15],
        "outliers_evergreen": [slim(r) for r in top if r in old][:5],
    }


def slim(r):
    return {k: r[k] for k in ("platform", "format", "outlier_x", "engagement", "likes", "comments", "shares",
                              "views", "followers", "age_days", "author", "url")} | {
        "hook": hook(r["text"]), "text": r["text"][:400]}


def compare(cur, prev):
    if not prev:
        return None
    def share(items, key):
        tot = sum(i["engagement"] for i in items) or 1
        return {i[key]: i["engagement"] / tot for i in items}
    out = {}
    for name, key in (("top_hashtags", "tag"), ("top_phrases", "phrase")):
        a, b = share(cur[name], key), share(prev[name], key)
        out[name] = {
            "baru": [k for k in a if k not in b][:10],
            "naik": [k for k in sorted(a, key=lambda k: -(a[k] - b.get(k, 0))) if k in b and a[k] > b[k]][:10],
            "turun": [k for k in b if k not in a][:10],
        }
    return out


def to_md(s, cfg, run, prev_run, cmp):
    L = [f"# Ringkasan data tren: {run}", "",
         f"Niche: {cfg.get('niche')}  ",
         f"Keyword: {', '.join(cfg['keywords'])} | Hashtag: {', '.join(cfg.get('hashtags', []))}  ",
         f"Total {s['total_posts']} post unik; {s['recent_posts']} dalam {s['days_back']} hari terakhir, "
         f"{s['old_posts']} lebih lama (evergreen).", ""]
    L += ["## Per platform", "", "| Platform | Post | Baru | Median engagement | Format terbaik (median) |",
          "|---|---|---|---|---|"]
    for p, v in s["platforms"].items():
        f = ", ".join(f"{k} {int(x['median_engagement'])} ({x['posts']})" for k, x in v["formats"].items())
        L.append(f"| {p} | {v['posts']} | {v['recent_posts']} | {int(v['median_engagement'])} | {f} |")
    for p, v in s["platforms"].items():
        L += ["", f"## Bahan tren {p.upper()} ({v['recent_posts']} post baru)", ""]
        if v["top_hashtags"]:
            L.append("Hashtag: " + ", ".join(f"#{t['tag']} ({t['posts']})" for t in v["top_hashtags"]))
        if v["top_phrases"]:
            L.append("Frasa berulang: " + ", ".join(f"\"{t['phrase']}\" ({t['posts']})" for t in v["top_phrases"]))
        L.append("Post teratas (baru):")
        for r in v["top_recent"]:
            L.append(f"- {r['outlier_x']}x · {r['format']} · {r['engagement']} eng · {r['age_days']} hari · "
                     f"@{r['author']} · {r['url']}\n  {r['text'][:220]}")
        if not v["top_recent"]:
            L.append("- (tidak ada post baru di periode ini)")
    L += ["", "## Hashtag pembawa engagement (di luar hashtag pencarian & generik)", ""]
    L += [f"- #{t['tag']}: {t['posts']} post, total engagement {t['engagement']}" for t in s["top_hashtags"][:15]]
    L += ["", "## Frasa yang sering muncul di post (≥2 post)", ""]
    L += [f"- \"{t['phrase']}\": {t['posts']} post, engagement {t['engagement']}" for t in s["top_phrases"][:15]]
    if cmp:
        L += ["", f"## Dibanding run sebelumnya ({prev_run})", ""]
        for name, label in (("top_hashtags", "Hashtag"), ("top_phrases", "Frasa")):
            c = cmp[name]
            L.append(f"- {label} baru: {', '.join(c['baru']) or '-'}")
            L.append(f"- {label} naik: {', '.join(c['naik']) or '-'}")
            L.append(f"- {label} hilang: {', '.join(c['turun']) or '-'}")
    L += ["", f"## Post outlier, {s['days_back']} hari terakhir (outlier_x = kali lipat dari median platformnya, minimal dibagi 20)", ""]
    for r in s["outliers_recent"]:
        L.append(f"- **{r['platform']}/{r['format']}** {r['outlier_x']}x · {r['engagement']} eng · "
                 f"{r['age_days']} hari · @{r['author']} ({r['followers'] or '?'} followers) · {r['url']}")
        L.append(f"  - Hook: \"{r['hook']}\"")
        L.append(f"  - Isi: {r['text'][:300]}")
    if s["outliers_evergreen"]:
        L += ["", "## Post lama yang masih kuat (evergreen, bukan tren baru)", ""]
        for r in s["outliers_evergreen"]:
            L.append(f"- {r['platform']}/{r['format']} {r['outlier_x']}x · {r['age_days']} hari · "
                     f"\"{r['hook']}\" · {r['url']}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="nama folder di data/ (default: terbaru)")
    args = ap.parse_args()

    all_runs = runs()
    if not all_runs:
        raise SystemExit("Belum ada data. Jalankan dulu: python3 collect.py")
    run_dir = DATA / args.run if args.run else all_runs[-1]
    idx = all_runs.index(run_dir)
    prev_dir = all_runs[idx - 1] if idx > 0 else None

    cfg = collect.load_config()
    cur = analyze(load_rows(run_dir), cfg)
    prev = analyze(load_rows(prev_dir), cfg) if prev_dir else None
    cmp = compare(cur, prev)
    cur["compare_with"] = prev_dir.name if prev_dir else None
    cur["compare"] = cmp

    (run_dir / "summary.json").write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
    (run_dir / "summary.md").write_text(
        to_md(cur, cfg, run_dir.name, prev_dir.name if prev_dir else None, cmp), encoding="utf-8")
    print(f"✓ {cur['total_posts']} post dianalisis → {run_dir.relative_to(ROOT)}/summary.md")


if __name__ == "__main__":
    main()
