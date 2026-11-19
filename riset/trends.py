#!/usr/bin/env python3
"""Ambil Google Trends harian Indonesia (gratis, tanpa token) untuk Radar Topik pilar 2.

Pakai:
  python3 trends.py            # simpan ke data/<tanggal>_trends/ (trends.json + trends.md)
  python3 trends.py --geo ID   # negara lain kalau perlu

Sumber: RSS https://trends.google.com/trending/rss?geo=ID (butuh host trends.google.com diizinkan di environment).
RSS hanya berisi tren ~24 jam terakhir, jadi jalankan beberapa kali seminggu (atau tiap riset) supaya
gambaran mingguannya lengkap; hasil tiap hari disimpan terpisah dan digabung oleh Lira.
"""
import argparse, datetime, json, os, re, urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
NS = {"ht": "https://trends.google.com/trending/rss"}


def traffic_num(s):
    m = re.match(r"([\d.,]+)\s*([KMkm]?)", (s or "").replace("+", ""))
    if not m:
        return 0
    n = float(m.group(1).replace(",", ""))
    return int(n * {"k": 1e3, "m": 1e6}.get(m.group(2).lower(), 1))


def fetch(geo):
    req = urllib.request.Request(f"https://trends.google.com/trending/rss?geo={geo}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    out = []
    for it in root.iter("item"):
        news = [{"judul": n.findtext("ht:news_item_title", "", NS), "sumber": n.findtext("ht:news_item_source", "", NS),
                 "url": n.findtext("ht:news_item_url", "", NS)} for n in it.findall("ht:news_item", NS)]
        tr = it.findtext("ht:approx_traffic", "", NS)
        out.append({"kata": it.findtext("title", ""), "trafik": tr, "trafik_angka": traffic_num(tr),
                    "waktu": it.findtext("pubDate", ""), "berita": news})
    out.sort(key=lambda x: -x["trafik_angka"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", default="ID")
    a = ap.parse_args()
    items = fetch(a.geo)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    od = os.path.join(HERE, "data", f"{stamp}_trends")
    os.makedirs(od, exist_ok=True)
    json.dump(items, open(os.path.join(od, "trends.json"), "w"), ensure_ascii=False, indent=1)
    lines = [f"# Google Trends {a.geo} — {stamp}", "", "| # | Kata kunci | Trafik | Berita teratas |", "|---|---|---|---|"]
    for i, t in enumerate(items, 1):
        b = t["berita"][0] if t["berita"] else {}
        lines.append(f"| {i} | {t['kata']} | {t['trafik']} | {b.get('judul', '')} ({b.get('sumber', '')}) |")
    open(os.path.join(od, "trends.md"), "w").write("\n".join(lines) + "\n")
    print(f"✓ {len(items)} tren → {os.path.relpath(od, HERE)}/trends.md")


if __name__ == "__main__":
    main()
