#!/usr/bin/env python3
"""Render post Instagram brand (1080x1350) dari spec JSON -> PNG, pakai Chrome headless.

Pakai:  python3 konten/brand/visual/render.py <spec.json>
        python3 konten/brand/visual/render.py <spec.json> --zones   # ukur area teks -> kalimat komposisi untuk prompt ilustrasi
Spec:
{
  "output_dir": "konten/visual/2026-11-23_F1",     # relatif ke root proyek
  "slides": [ { ...slide... }, ... ]                 # 1 slide = feed foto, >1 = carousel
}
Slide:
  layout      "foto-atas" (gaya Seakun: foto di atas memudar ke kertas, kotak judul oranye, subjudul, isi rata kanan-kiri)
              | "kiri" (teks kiri-atas, ilustrasi kanan/bawah) | "tengah" (judul di tengah atas)
              | "threads" (kartu kutipan Threads di atas ilustrasi)
  bg          nama latar dari brand.json "backgrounds" (default: latar pertama)
  illustration path PNG/JPG/WEBP ilustrasi (full-bleed, tanpa teks). Opsional.
  flip        true = cermin ilustrasi kiri-kanan (kalau tokoh ada di sisi teks)
  ill_zoom    mis. 1.2 = perbesar ilustrasi (tokoh lebih besar); ill_origin titik jangkar, default "right bottom" ("center bottom" untuk tengah)
  veil        "kiri" | "atas" | "none"         (gradasi supaya teks terbaca; default sesuai layout)
  veil_until  persen tinggi tempat veil hilang (kiri default 62, atas default 55)
  headline    judul (font judul brand). Markup: __teks__ = warna aksen, ~~teks~~ = abu gelap, \n = baris baru
  headline_size  px, default 100
  subhead     kalimat tebal warna primer di bawah judul (opsional)
  body        list paragraf. Markup: ==teks== = stabilo (highlight), **teks** = primer tebal, __teks__ = aksen tebal
  body_width  px lebar kolom teks, default 520 (kiri) / 900 (tengah)
  items       [{"icon":"heart","color":"primary|accent|highlight","text":"..."}]  daftar berikon (alias lama: pink|teal|yellow)
  items_cols  1 (default) atau 2: daftar jadi 2 kolom (hemat tinggi, pakai body_width lebar)
  cta_width   px lebar teks CTA (default = body_width)
  badge       {"type":"mitos|fakta","text":"..."}  kartu mitos/fakta
  cta         teks CTA berikon (markup sama dengan body); cta_icon default "bookmark" (mis. "share")
  body_size   px ukuran teks isi (default 27); body_gap px jarak ekstra judul -> teks isi
  threads     {"name":"..","avatar":"path opsional","verified":true,"text":["para1","para2"],"stats":["7.2K","304","2.3K","974"]}
  header      true/false (logo kiri atas + tagline kanan atas). Default true
  footer      "kunjungi" (label "Kunjungi website seakun.id") | "web-ig" | "logo-ig" | "none"; default dari brand.json footer_default
  --- khusus foto-atas ---
  foto        path foto/cuplikan (diisi user); foto_height px (default 790); foto_pos object-position (default "center top")
  judul       teks di kotak oranye, mis. "1. Pablo Escobar"
  subjudul    mis. "__Narcos__ (2015-2017)"  (__teks__ = hijau, sisanya hitam)
  text_top    px posisi atas kotak judul (default 672)
  nomor       angka di titik nomor kanan atas (default = urutan slide)
Ikon: share, heart, clock, users, smile, check, bookmark, chat, moon, star, book, alert, x, globe, instagram,
      droplet, trending-down, battery, scale, baby, sun, shield
Tanda kutip lurus "..." otomatis jadi kutip melengkung “...”. Teks memakai text-wrap:pretty (anti 1 kata sendirian di baris terakhir).
"""
import html, json, os, re, subprocess, sys, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CHROME = next((c for c in [os.environ.get("CHROME_PATH", ""),
                           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                           shutil.which("google-chrome") or "", shutil.which("chromium") or "",
                           "/opt/pw-browsers/chromium"] if c and os.path.exists(c)),
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CHROME_EXTRA = ["--no-sandbox"] if hasattr(os, "geteuid") and os.geteuid() == 0 else []  # Chrome menolak jalan sebagai root tanpa ini
W, H = 1080, 1350

# Identitas brand (warna, font, logo, tagline, footer) dibaca dari brand.json di folder ini.
_bp = os.path.join(HERE, "brand.json")
if not os.path.exists(_bp):
    sys.exit("brand.json belum ada di konten/brand/visual/. Jalankan setup brand dulu.")
BRAND = json.load(open(_bp, encoding="utf-8"))
_c = BRAND["colors"]
C = {"pink": _c["primary"], "pink2": _c["secondary"], "teal": _c["accent"], "teal_dark": _c["accent_dark"],
     "yellow": _c["highlight"], "text": _c["text"], "soft": _c.get("primary_soft", _c["secondary"]),
     "label": _c.get("label", _c["accent"])}
BG = BRAND["backgrounds"]
BG_DEFAULT = next(iter(BG))

I = {
 "heart": '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
 "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
 "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>',
 "check": '<polyline points="20 6 9 17 4 12"/>',
 "bookmark": '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
 "chat": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>',
 "moon": '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>',
 "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
 "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
 "alert": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
 "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
 "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
 "droplet": '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>',
 "trending-down": '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>',
 "battery": '<rect x="1" y="6" width="18" height="12" rx="2" ry="2"/><line x1="23" y1="13" x2="23" y2="11"/><line x1="5" y1="10" x2="5" y2="14"/>',
 "scale": '<path d="M12 3v18"/><path d="M5 21h14"/><path d="M3 7h18"/><path d="M6 7l-3 7a3 3 0 0 0 6 0z"/><path d="M18 7l-3 7a3 3 0 0 0 6 0z"/>',
 "baby": '<circle cx="12" cy="8" r="5"/><path d="M3 21v-1a7 7 0 0 1 7-7h4a7 7 0 0 1 7 7v1"/><path d="M10 8h.01"/><path d="M14 8h.01"/>',
 "sun": '<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
 "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
 "instagram": '<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>',
}

def icon(name, size=40, stroke="#fff", width=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{I.get(name, I["heart"])}</svg>')

def uri(p):
    if not p:
        return ""
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    if not os.path.exists(p):
        sys.exit(f"File tidak ditemukan: {p}")
    return "file://" + p

def curly(s):
    s = re.sub(r'"([^"]*)"', "\u201c\\1\u201d", s)
    return s.replace("'", "\u2019")

def md(s):
    s = html.escape(curly(s), quote=False)
    s = re.sub(r"^==([\s\S]+?)==$", r'<span class="hl pill">\1</span>', s)
    s = re.sub(r"==([\s\S]+?)==", r'<span class="hl">\1</span>', s)
    s = re.sub(r"\*\*([\s\S]+?)\*\*", r'<b class="pk">\1</b>', s)
    s = re.sub(r"__([\s\S]+?)__", r'<b class="tl">\1</b>', s)
    s = re.sub(r"~~([\s\S]+?)~~", r'<span class="dk">\1</span>', s)
    return s.replace("\n", "<br>")

def head(s):
    s = html.escape(curly(s), quote=False)
    s = re.sub(r"__([\s\S]+?)__", r'<span class="tl">\1</span>', s)
    s = re.sub(r"~~([\s\S]+?)~~", r'<span class="dk">\1</span>', s)
    return s.replace("\n", "<br>")

CSS = """
%(fontfaces)s
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:%(W)spx;height:%(H)spx;overflow:hidden}
body{font-family:BodyFont,sans-serif;color:%(text)s;position:relative}
.ill{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.veil{position:absolute;inset:0}
.hdr{position:absolute;top:66px;left:76px;right:70px;display:flex;justify-content:space-between;align-items:center;z-index:3}
.hdr img{height:46px}
.tag{text-align:right;color:%(pink)s;font-size:19px;line-height:1.25}
.tag b{font-weight:700}
.wrap{position:absolute;z-index:2}
.kiri .wrap{top:222px;left:72px}
.tengah .wrap{top:205px;left:0;right:0;text-align:center;display:flex;flex-direction:column;align-items:center}
.h{font-family:HeadFont,sans-serif;color:%(pink)s;line-height:1.02;letter-spacing:.5px}
.h .tl{color:%(teal_dark)s}.h .dk{color:#3d3d3d}
.sub{color:%(pink)s;font-weight:700;font-size:27px;line-height:1.4;margin-top:30px;text-wrap:pretty}
.body p{font-size:27px;line-height:1.45;margin-top:26px;letter-spacing:.2px;text-wrap:pretty}
.hl.pill{padding:3px 26px}
.hl{background:%(yellow)s;color:#2f2f2f;font-weight:700;border-radius:22px;padding:2px 12px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.pk{color:%(pink)s;font-weight:700}.tl{color:%(teal_dark)s;font-weight:700}.dk{color:#2f2f2f}
.items{margin-top:36px}
.it{display:flex;align-items:center;gap:22px;padding:18px 0;border-bottom:2px dashed %(teal)s}
.it:last-child{border-bottom:none}
.items.grid .it:nth-last-child(2):nth-child(odd){border-bottom:none}
.dot{flex:none;width:60px;height:60px;border-radius:50%%;display:flex;align-items:center;justify-content:center}
.it span{font-size:25px;line-height:1.35;text-wrap:pretty}
.badge{margin-top:76px;width:840px;border:3px dashed %(pink2)s;border-radius:40px;background:rgba(255,239,243,.88);padding:64px 44px 40px;position:relative}
.badge.fakta{border-color:%(teal)s;background:rgba(232,248,245,.9)}
.badge .lbl{position:absolute;top:-52px;left:50%%;transform:translateX(-50%%);display:flex;align-items:center}
.badge .lbl .c{width:96px;height:96px;border-radius:50%%;display:flex;align-items:center;justify-content:center;border:8px solid #fff;z-index:2}
.badge .lbl .t{margin-left:-26px;padding:14px 40px 14px 46px;color:#fff;font-family:HeadFont,sans-serif;font-size:50px;border-radius:0 18px 18px 0}
.badge .txt{font-size:37px;font-weight:600;line-height:1.3;color:#2f2f2f;text-align:center;text-wrap:pretty}
.cta{display:flex;align-items:center;gap:20px;margin-top:36px}
.cta .dot{width:60px;height:60px;background:%(yellow)s}
.cta span{font-size:23px;line-height:1.45;color:%(pink)s;text-wrap:pretty;text-align:left}
.card{position:absolute;z-index:2;top:104px;left:50%%;transform:translateX(-50%%);width:610px;background:#fff;border-radius:30px;box-shadow:0 10px 40px rgba(0,0,0,.08);padding:30px 40px 34px}
.card .who{display:flex;align-items:center;gap:16px;font-weight:700;font-size:22px;color:#111}
.card .av{width:56px;height:56px;border-radius:50%%;background:%(pink2)s;object-fit:cover}
.card .vf{width:18px;height:18px;border-radius:50%%;background:#3897f0;display:inline-block}
.card p{font-size:22px;line-height:1.55;color:#222;margin-top:18px}
.card .st{display:flex;gap:46px;margin-top:26px;font-size:20px;color:#333}
.card .st span:first-child{color:#e0245e}
.ftr{position:absolute;right:0;bottom:66px;z-index:3;background:%(pink)s;color:#fff;border-radius:40px 0 0 40px;height:62px;padding:0 32px 0 32px;display:flex;align-items:center;gap:12px;font-size:27px;font-weight:500}
.ftr img{height:34px}
.ftr .sep{opacity:.9;margin:0 6px}
/* ---- gaya Seakun: badge logo + titik nomor slide, foto-atas, label kunjungi ---- */
.hdr2{position:absolute;top:58px;left:74px;right:86px;display:flex;justify-content:space-between;align-items:center;z-index:3}
.hdr2 .bdg{width:96px;height:96px;margin:6px}
.dots{display:flex;align-items:center}
.dots i{width:57px;height:57px;border-radius:50%%;margin-left:-28px;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:HeadFont,sans-serif;color:#fff;font-size:34px}
.dots i:first-child{margin-left:0}
.foto{position:absolute;left:0;top:0;width:100%%;object-fit:cover;-webkit-mask-image:linear-gradient(180deg,#000 0%%,#000 62%%,transparent 98%%)}
.fa{position:absolute;z-index:2;left:108px;right:108px}
.fa .jdl{display:inline-block;background:%(label)s;color:#fff;font-family:HeadFont,sans-serif;font-size:64px;line-height:1.12;padding:2px 44px 2px 22px}
.fa .sbj{font-family:HeadFont,sans-serif;font-size:47px;line-height:1.25;color:#111;margin-top:28px;text-wrap:pretty}
.fa .sbj .g{color:%(pink)s}
.fa .isi p{font-size:30px;line-height:1.43;text-align:justify;margin-top:42px;letter-spacing:.1px}
.fa .isi p+p{margin-top:20px}
.fa .isi b{font-weight:700}
.kjg{position:absolute;z-index:3;left:50%%;transform:translateX(-50%%);bottom:64px;display:flex;align-items:center;gap:18px;white-space:nowrap;background:#fff;border-radius:60px;padding:9px 9px 9px 40px;box-shadow:0 8px 28px rgba(0,0,0,.10)}
.kjg .t{font-weight:700;font-size:30px;color:%(pink)s}
.kjg .w{background:%(pink)s;color:#fff;font-weight:700;font-size:30px;border-radius:50px;padding:12px 34px}
"""

def fontfaces():
    fd = "file://" + os.path.join(HERE, "font")
    f = BRAND["fonts"]
    out = [f"@font-face{{font-family:HeadFont;src:url('{fd}/{f['heading']}')}}"]
    for w, fn in f["body"].items():
        out.append(f"@font-face{{font-family:BodyFont;font-weight:{w};src:url('{fd}/{fn}')}}")
    return "\n".join(out).replace("%", "%%")

def badge_svg():
    """Badge logo bulat: teks melingkar 'PLATFORM PATUNGAN #1' + website, ikon di tengah."""
    ik = uri(BRAND.get("logo_ikon", BRAND["logo_header"]))
    atas = html.escape(BRAND.get("badge_atas", "PLATFORM PATUNGAN #1"))
    bawah = html.escape(BRAND.get("badge_bawah", BRAND["website"]))
    return (f'<svg class="bdg" viewBox="0 0 100 100" overflow="visible"><defs>'
            f'<path id="ba" d="M 12,50 A 38,38 0 1,1 88,50 A 38,38 0 1,1 12,50"/>'
            f'<path id="bb" d="M 14,50 A 36,36 0 0,0 86,50"/></defs>'
            f'<image href="{ik}" x="22" y="22" width="56" height="56"/>'
            f'<text font-family="BodyFont" font-weight="700" font-size="8.6" fill="#1d1d1d" letter-spacing=".5">'
            f'<textPath href="#ba" startOffset="4">{atas}</textPath></text>'
            f'<text font-family="HeadFont" font-size="15" fill="{C["pink"]}" letter-spacing=".2" dominant-baseline="hanging">'
            f'<textPath href="#bb" startOffset="50%" text-anchor="middle">{bawah}</textPath></text></svg>')

def dots_html(n):
    cols = BRAND.get("dots", [C["pink"], "#2FBFA5", "#4AD1B9", "#7AEBD6", "#AAFFEF"])
    out = []
    for k, c in enumerate(cols):
        out.append(f'<i style="background:{c};z-index:{len(cols)-k}">{n if k == 0 else ""}</i>')
    return '<div class="dots">' + "".join(out) + "</div>"

def green(s):
    s = html.escape(curly(s), quote=False)
    s = re.sub(r"__([\s\S]+?)__", r'<span class="g">\1</span>', s)
    return s.replace("\n", "<br>")

def slide_html(s, n=1):
    layout = s.get("layout", "kiri")
    bg = BG.get(s.get("bg", BG_DEFAULT), BG[BG_DEFAULT])
    veil = s.get("veil", {"kiri": "kiri", "tengah": "atas", "threads": "none", "foto-atas": "none"}.get(layout, "kiri"))
    vstop = s.get("veil_until", 62 if veil == "kiri" else 55)
    vcss = {"kiri": f"linear-gradient(90deg,{bg} 0%,{bg}EE 38%,{bg}00 62%)",
            "atas": f"linear-gradient(180deg,{bg} 0%,{bg}F0 {vstop-21}%,{bg}00 {vstop}%)",
            "none": "none"}[veil]
    tex = BRAND.get("texture") if s.get("texture", True) else None
    bgcss = f"background:{bg} url('{uri(tex)}') center/cover no-repeat" if tex else f"background:{bg}"
    out = [f'<body class="{layout}" style="{bgcss}">']
    if layout == "foto-atas" and s.get("foto"):
        out.append(f'<img class="foto" src="{uri(s["foto"])}" style="height:{s.get("foto_height", 790)}px;object-position:{s.get("foto_pos", "center top")}">')
    if s.get("illustration"):
        tf = []
        if s.get("flip"): tf.append("scaleX(-1)")
        if s.get("ill_zoom"): tf.append(f"scale({s['ill_zoom']})")
        fl = (f' style="transform:{" ".join(tf)};transform-origin:{s.get("ill_origin","right bottom")}"' if tf else "")
        out.append(f'<img class="ill" src="{uri(s["illustration"])}"{fl}>')
    # veil kiri hanya di area teks: memudar ke bawah supaya ilustrasi kiri-bawah tetap terlihat
    mask = (f"-webkit-mask-image:linear-gradient(180deg,#000 0%,#000 {vstop-14}%,transparent {vstop+8}%);"
            if veil == "kiri" else "")
    out.append(f'<div class="veil" style="background:{vcss};{mask}"></div>')
    if s.get("header", True) and BRAND.get("header_style") == "seakun":
        out.append(f'<div class="hdr2">{badge_svg()}{dots_html(n)}</div>')
    elif s.get("header", True) and layout != "threads":
        out.append(f'<div class="hdr"><img src="{uri(BRAND["logo_header"])}">'
                   f'<div class="tag">{BRAND.get("tagline_html", "")}</div></div>')
    if layout == "threads" and s.get("threads"):
        t = s["threads"]
        av = f'<img class="av" src="{uri(t["avatar"])}">' if t.get("avatar") else '<div class="av"></div>'
        vf = '<span class="vf"></span>' if t.get("verified") else ""
        paras = "".join(f"<p>{md(p)}</p>" for p in t.get("text", []))
        st = t.get("stats", [])
        stats = ""
        if st:
            lab = ["♥ ", "💬 ", "🔁 ", "➤ "]
            stats = '<div class="st">' + "".join(f"<span>{lab[i]}{html.escape(v)}</span>" for i, v in enumerate(st[:4])) + "</div>"
        out.append(f'<div class="card"><div class="who">{av}{html.escape(t.get("name",""))} {vf}</div>{paras}{stats}</div>')
    elif layout != "foto-atas":
        bw = s.get("body_width", 900 if layout == "tengah" else 520)
        parts = []
        if s.get("headline"):
            parts.append(f'<div class="h" style="font-size:{s.get("headline_size",100)}px">{head(s["headline"])}</div>')
        if s.get("subhead"):
            parts.append(f'<div class="sub" style="max-width:{bw}px">{md(s["subhead"])}</div>')
        if s.get("badge"):
            b = s["badge"]; m = b.get("type") == "mitos"
            col = C["pink"] if m else C["teal_dark"]
            parts.append(f'<div class="badge {"mitos" if m else "fakta"}"><div class="lbl"><div class="c" style="background:{col}">{icon("x" if m else "check",46,"#fff",3.2)}</div>'
                         f'<div class="t" style="background:{col}">{"MITOS" if m else "FAKTA"}</div></div>'
                         f'<div class="txt">{md(b.get("text",""))}</div></div>')
        if s.get("body"):
            bsz = f"font-size:{s['body_size']}px;" if s.get("body_size") else ""
            gap = f"margin-top:{s['body_gap']}px;" if s.get("body_gap") else ""
            parts.append(f'<div class="body" style="max-width:{bw}px;{gap}">' + "".join(f'<p style="{bsz}">{md(p)}</p>' for p in s["body"]) + "</div>")
        if s.get("items"):
            rows = []
            for it in s["items"]:
                col = {"pink": C["soft"], "primary": C["soft"], "teal": C["teal"], "accent": C["teal"], "yellow": C["yellow"], "highlight": C["yellow"]}.get(it.get("color", "primary"), C["soft"])
                stroke = C["pink"] if col == C["yellow"] else "#fff"  # ikon putih tak terbaca di stabilo pucat
                rows.append(f'<div class="it"><div class="dot" style="background:{col}">{icon(it.get("icon","heart"),30,stroke,2.4)}</div><span>{md(it["text"])}</span></div>')
            cols = s.get("items_cols", 1)
            grid = f"display:grid;grid-template-columns:repeat({cols},1fr);column-gap:34px;" if cols > 1 else ""
            parts.append(f'<div class="items{" grid" if cols > 1 else ""}" style="width:{bw}px;{grid}">' + "".join(rows) + "</div>")
        if s.get("cta"):
            parts.append(f'<div class="cta"><div class="dot">{icon(s.get("cta_icon","bookmark"),30,C["pink"],2.4)}</div><span style="max-width:{s.get("cta_width", bw)}px">{md(s["cta"])}</span></div>')
        out.append('<div class="wrap">' + "".join(parts) + "</div>")
    if layout == "foto-atas":
        parts = []
        if s.get("judul"):
            parts.append(f'<div><span class="jdl">{html.escape(curly(s["judul"]))}</span></div>')
        if s.get("subjudul"):
            parts.append(f'<div class="sbj">{green(s["subjudul"])}</div>')
        if s.get("body"):
            parts.append('<div class="isi">' + "".join(f'<p>{md(p)}</p>' for p in s["body"]) + "</div>")
        out.append(f'<div class="fa" style="top:{s.get("text_top", 672)}px">' + "".join(parts) + "</div>")
    f = s.get("footer", BRAND.get("footer_default", "web-ig"))
    if f == "kunjungi":
        out.append(f'<div class="kjg"><span class="t">Kunjungi website</span><span class="w">{html.escape(BRAND["website"])}</span></div>')
    elif f == "web-ig":
        out.append(f'<div class="ftr">{icon("globe",30,"#fff",2)} {html.escape(BRAND["website"])} <span class="sep">|</span> {icon("instagram",30,"#fff",2)} @{html.escape(BRAND["handle"])}</div>')
    elif f == "logo-ig":
        out.append(f'<div class="ftr"><img src="{uri(BRAND["logo_footer"])}"><span class="sep">|</span> @{html.escape(BRAND["handle"])}</div>')
    out.append("</body>")
    css = CSS % dict(C, fontfaces=fontfaces(), W=W, H=H)
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>{"".join(out)}</html>'

MEASURE_JS = """<script>
document.fonts.ready.then(()=>{
function box(el){let L=1e9,T=1e9,R=-1,B=-1;const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;
while(n=walk.nextNode()){if(!n.textContent.trim())continue;const r=document.createRange();r.selectNodeContents(n);
for(const c of r.getClientRects()){L=Math.min(L,c.left);T=Math.min(T,c.top);R=Math.max(R,c.right);B=Math.max(B,c.bottom);}}
el.querySelectorAll('.dot,.badge,.hl').forEach(e=>{const c=e.getBoundingClientRect();L=Math.min(L,c.left);T=Math.min(T,c.top);R=Math.max(R,c.right);B=Math.max(B,c.bottom);});
if(el.classList.contains('badge')){const c=el.getBoundingClientRect();L=Math.min(L,c.left);T=Math.min(T,c.top-52);R=Math.max(R,c.right);B=Math.max(B,c.bottom);}
return [L,T,R,B].map(Math.round).join(',');}
const w=document.querySelector('.wrap');const res=[];
if(w){for(const ch of w.children){res.push((ch.classList.contains('h')?'H':'X')+':'+box(ch));}}
document.title='BOX|'+res.join('|');
});
</script>"""

def zones(spec):
    """Ukur area teks tiap slide (tanpa ilustrasi) -> kalimat komposisi siap tempel untuk prompt ilustrasi + peringatan."""
    tmp = tempfile.mkdtemp()
    out = []
    pct = lambda v, tot: round(v / tot * 100)
    for i, s in enumerate(spec["slides"], 1):
        s2 = {k: v for k, v in s.items() if k != "illustration"}
        hp = os.path.join(tmp, f"m{i}.html")
        open(hp, "w").write(slide_html(s2).replace("</body>", MEASURE_JS + "</body>"))
        r = subprocess.run([CHROME, "--headless=new", *CHROME_EXTRA, "--disable-gpu", "--allow-file-access-from-files",
                            f"--user-data-dir={tmp}/u", f"--window-size={W},{H}", "--virtual-time-budget=3000",
                            "--dump-dom", "file://" + hp], capture_output=True, text=True)
        m = re.search(r"<title>BOX\|([^<]*)</title>", r.stdout)
        if not m or not m.group(1):
            out.append(dict(slide=i, layout=s.get("layout"), text="(tidak ada teks terukur)", warn=[])); continue
        boxes = []
        for part in m.group(1).split("|"):
            kind, nums = part.split(":")
            l, t, rr, b = map(int, nums.split(","))
            if rr > 0:
                boxes.append((kind, l, t, rr, b))
        hb = [b for b in boxes if b[0] == "H"]; xb = [b for b in boxes if b[0] != "H"]
        M = 5  # margin aman (%)
        warn = []
        if s.get("layout") == "tengah" or s.get("veil") == "atas":
            bottom = min(95, pct(max(b[4] for b in boxes), H) + M)
            sent = (f"Keep the ENTIRE UPPER {bottom}% of the image (full width, from the top edge down to {bottom}% of the height) "
                    f"as an empty plain softly lit background: nothing in it (no people, no furniture, no plants, no wall decor). "
                    f"All characters and objects stay in the LOWER {100-bottom}%; the top of every head, hair bun and raised hand must be below {bottom}% height. "
                    f"Make the characters LARGE so they fill that lower area: the tallest head should be just below {bottom}% height, the group spans most of the width (about 15% to 85%), feet near the bottom edge. Do not make them small or leave a big empty gap below the text area.")
            if bottom > 60:
                warn.append(f"teks sampai {bottom}% tinggi: ruang tokoh tinggal {100-bottom}% bawah. Ringkas copy / kecilkan judul / pakai items_cols 2")
        else:
            h_r = min(95, pct(max(b[3] for b in hb), W) + M) if hb else 0
            h_b = min(95, pct(max(b[4] for b in hb), H) + M) if hb else 15
            x_r = min(95, pct(max(b[3] for b in xb), W) + M) if xb else 0
            x_b = min(95, pct(max(b[4] for b in xb), H) + M) if xb else h_b
            parts = [f"(1) a band from the TOP edge down to {h_b}% of the height, covering the LEFT {max(h_r, x_r)}% of the width"]
            if xb:
                parts.append(f"(2) below that, the LEFT {x_r}% of the width down to {x_b}% of the height")
            sent = ("Keep these areas completely EMPTY, plain softly lit wall with nothing in front of it (no people, no furniture, no plants, no frames): "
                    + "; ".join(parts) + ". "
                    + f"Characters and objects go ONLY to the right of {x_r if xb else h_r}% width, or below {x_b}% height. "
                    + "No head, hair, hand or object may enter the empty areas. "
                    + f"Make the characters LARGE so they fill the allowed area: the group spans from about {(x_r if xb else h_r)+2}% to 98% of the width, the tallest head starts just below {h_b}% height, and the figures reach close to the bottom edge. Do not make them small.")
            free_right = 100 - (x_r if xb else h_r)
            if free_right < 38 and x_b > 60:
                warn.append(f"ruang tokoh sempit: kanan cuma {free_right}% dan teks turun sampai {x_b}%. Ringkas copy, pakai items_cols 2, atau kecilkan body_width")
            if h_r > 85 and x_b > 55:
                warn.append(f"judul hampir selebar slide ({h_r}%): tokoh harus di bawah {h_b}%. Pertimbangkan judul lebih pendek / 2 baris")
        out.append(dict(slide=i, layout=s.get("layout"), text=sent, warn=warn))
    shutil.rmtree(tmp, ignore_errors=True)
    return out

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec = json.load(open(sys.argv[1]))
    if "--zones" in sys.argv:
        for z in zones(spec):
            print(f"--- slide {z['slide']} ({z['layout']})")
            print(f"Composition: {z['text']}")
            for w in z["warn"]:
                print(f"  ⚠ {w}")
        return
    od = spec["output_dir"]
    od = od if os.path.isabs(od) else os.path.join(ROOT, od)
    os.makedirs(od, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for i, s in enumerate(spec["slides"], 1):
        hp = os.path.join(od, f"slide-{i:02d}.html")
        open(hp, "w").write(slide_html(s, s.get("nomor", i)))
        png = os.path.join(od, f"slide-{i:02d}.png")
        subprocess.run([CHROME, "--headless=new", *CHROME_EXTRA, "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1",
                        f"--user-data-dir={tmp}", f"--window-size={W},{H}",
                        "--virtual-time-budget=3000", f"--screenshot={png}", "file://" + hp],
                       check=True, capture_output=True)
        print("✓", os.path.relpath(png, ROOT))
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
