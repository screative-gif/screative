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
  --- slide data ("data") & CTA ("cta-seakun") untuk format "cerita di balik" ---
  data: gambar (path foto, opsional; gambar_tinggi px default 430, gambar_pos), judul (__x__ = hijau + stabilo oranye), isi [paragraf], penutup, sumber (tampil di bar bawah: "Sumber: …"),
        visual {"tipe": "angka-besar" (angka, ket | pembanding:[{angka,ket,warna:"oranye"}]) | "batang" (judul, items:[{label,nilai,teks,sorot:"hijau|oranye"}])
                | "dulu-vs-sekarang" (kiri/kanan:{judul,isi[]}) | "tabel" (kolom[], baris[[]], sorot_kolom) | "daftar" (items[])
                | "kutipan" (teks, oleh) | "notif" (jam, items:[{app,teks,rp:"+Rp…/−Rp…",akhir:true}])
                | "versus" (kiri/kanan:{label,angka,ket}, badge "+85%", catatan) — perbandingan 2 angka + panah
                | "balapan" (items:[{label,nilai,teks,warna:"hijau|kuning|oranye|gelap"}], garis:{nilai,teks}, anotasi) — batang + garis acuan
                | "turun" (angka, ket, pendamping:[{angka,ket}]) — angka turun + panah besar}
        gambar_mode: "atas" (default) | "polaroid" (foto kecil miring di pojok kanan atas, gambar_ket, gambar_miring)
                | "lingkaran" (badge bulat di pojok) | "sisi" (panel di samping judul) | "strip" (gambar: [3 path] berjejer)
  cta-seakun: jembatan, manfaat, gambar (opsional, gambar_tinggi default 300), layanan [nama disamarkan], ajakan_akhir; pakai bar_kanan:"ig" di slide terakhir
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
     "label": _c.get("label", _c["accent"]),
     "or": _c.get("oranye_terang", "#FF7A1A"), "kn": _c.get("kuning", "#FFC233"), "hj": _c.get("hijau_tua", "#0B5C4B"), "ink": "#17201D"}
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
 "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
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
.hl{background:#CDEFE6;color:#0B3D33;font-weight:700;border-radius:999px;padding:1px .45em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
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
/* ---- layout berita (cover = "berita", isi = "berita-isi") ---- */
.bfoto{position:absolute;left:0;top:0;width:100%%;object-fit:cover}
.bshade{position:absolute;left:0;right:0;top:0;height:260px;background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0))}
.hdr3{position:absolute;top:50px;left:0;right:0;z-index:3;display:flex;flex-direction:column;align-items:center;gap:8px}
.hdr3 img{height:46px}
.hdr3 .tg{color:#fff;font-weight:600;font-size:13.5px;letter-spacing:1.8px;text-transform:uppercase;display:flex;align-items:center;gap:10px;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.hdr3 .tg i{width:18px;height:2px;background:#fff;opacity:.8}
.hdr3.gelap img{filter:none}.hdr3.gelap .tg{color:%(pink)s;text-shadow:none}.hdr3.gelap .tg i{background:%(pink)s}
.kartu{position:absolute;z-index:2;left:56px;right:56px;background:#fff;border-radius:0 0 56px 0;padding:44px 48px 46px 48px;box-shadow:0 16px 44px rgba(0,0,0,.18)}
.kartu .strip{position:absolute;left:0;top:-12px;display:flex;height:12px}
.kartu .strip i{width:118px;height:12px}
.kartu .kick{display:inline-block;background:%(label)s;color:#fff;font-weight:700;font-size:21px;letter-spacing:1.5px;text-transform:uppercase;border-radius:8px;padding:6px 16px;margin-bottom:22px}
.kartu .bj{font-family:HeadFont,sans-serif;font-size:74px;line-height:1.1;color:#111;letter-spacing:-.5px;text-wrap:balance}
.kartu .bj .g{color:%(pink)s}
.kartu .bs{font-size:50px;line-height:1.2;color:#111;margin-top:10px;font-weight:400;text-wrap:balance}
/* varian kartu: stiker */
.kartu.stiker{border-radius:40px;padding:70px 50px 46px}
.kartu.stiker .kick{position:absolute;top:-24px;left:40px;transform:rotate(-4deg);margin:0;border-radius:12px;padding:9px 20px;font-size:22px;box-shadow:0 8px 18px rgba(255,79,47,.35);display:flex;align-items:center;gap:8px}
.kartu.stiker .bj .g{color:%(pink)s;background:linear-gradient(180deg,transparent 58%%,%(yellow)s 58%%,%(yellow)s 90%%,transparent 90%%);padding:0 6px;margin:0 -6px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.kartu .wm{position:absolute;right:-30px;bottom:-30px;width:230px;opacity:.07;pointer-events:none}
/* varian kartu: pita */
.kartu.pita{border-radius:34px;padding:0;overflow:hidden}
.kartu.pita .pt{height:66px;background:linear-gradient(100deg,%(pink)s,#2FBFA5 60%%,#7AEBD6);display:flex;align-items:center;justify-content:space-between;padding:0 30px 0 48px}
.kartu.pita .pt .kk{color:#fff;font-weight:700;font-size:21px;letter-spacing:2px;text-transform:uppercase;display:flex;align-items:center;gap:12px}
.kartu.pita .pt .kk i{width:10px;height:10px;border-radius:50%%;background:%(label)s;box-shadow:0 0 0 4px rgba(255,255,255,.35)}
.kartu.pita .pt .dd{display:flex;gap:7px}.kartu.pita .pt .dd i{width:14px;height:14px;border-radius:50%%;background:rgba(255,255,255,.55)}
.kartu.pita .pt .dd i:first-child{background:#fff}
.kartu.pita .bd{padding:38px 48px 46px}
.kartu.pita .bs{margin-top:24px}
.kartu.pita .bj .g{color:%(pink)s;text-decoration:underline wavy %(label)s;text-decoration-thickness:4px;text-underline-offset:14px;text-decoration-skip-ink:none}
/* varian tanpa kotak putih: gradasi & kaca */
.tgrad{position:absolute;left:0;right:0;bottom:0;height:72%%;z-index:1;background:linear-gradient(180deg,rgba(3,38,31,0) 0%%,rgba(3,38,31,.55) 38%%,rgba(3,38,31,.93) 78%%,rgba(3,38,31,.97) 100%%)}
.kartu.gradasi,.kartu.kaca{background:none;box-shadow:none;border-radius:0;top:auto!important;bottom:118px;padding:0 8px}
.kartu.gradasi .bj,.kartu.kaca .bj{color:#fff;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.kartu.gradasi .bj .g,.kartu.kaca .bj .g{color:#fff;background:linear-gradient(180deg,transparent 56%%,%(label)s 56%%,%(label)s 90%%,transparent 90%%);padding:0 8px;margin:0 -8px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.kartu.gradasi .bs,.kartu.kaca .bs{color:rgba(255,255,255,.92);font-size:44px;margin-top:14px}
.kartu.gradasi .kick,.kartu.kaca .kick{border-radius:30px;padding:8px 20px;display:inline-flex;align-items:center;gap:8px}
.kartu.gradasi .ln{width:90px;height:6px;border-radius:3px;background:linear-gradient(90deg,%(pink)s,#7AEBD6);margin-top:26px}
.kartu.kaca{padding:66px 46px 46px;border-radius:36px;background:linear-gradient(135deg,rgba(255,255,255,.26),rgba(255,255,255,.12));backdrop-filter:blur(20px) brightness(.78) saturate(150%%);-webkit-backdrop-filter:blur(20px) brightness(.78) saturate(150%%);border:1.5px solid rgba(255,255,255,.55);box-shadow:0 18px 50px rgba(0,0,0,.25),inset 0 1px 0 rgba(255,255,255,.55)}
.kartu.kaca .kick{position:absolute;top:-24px;left:40px;transform:rotate(-4deg);margin:0;border-radius:12px;padding:9px 20px;font-size:22px;box-shadow:0 8px 18px rgba(255,79,47,.35)}
.kartu.kaca .bj{text-shadow:0 2px 14px rgba(0,0,0,.30)}
.kartu.kaca .bj .g{color:#7AEBD6;background:linear-gradient(180deg,transparent 56%%,%(label)s 56%%,%(label)s 90%%,transparent 90%%);padding:0 8px;margin:0 -8px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.kartu.kaca .bs{text-shadow:0 1px 10px rgba(0,0,0,.35)}
/* varian tambahan: tiket, neo, strip (label miring di luar kotak) */
.kbox{position:absolute;z-index:2;left:56px;right:56px;bottom:118px}
.kbox .kick{position:absolute;z-index:3;top:-24px;left:40px;transform:rotate(-4deg);background:%(label)s;color:#fff;font-weight:700;font-size:22px;letter-spacing:1.5px;text-transform:uppercase;border-radius:12px;padding:9px 20px;box-shadow:0 8px 18px rgba(255,79,47,.35);display:flex;align-items:center;gap:8px}
.kbox .bj{font-family:HeadFont,sans-serif;font-size:74px;line-height:1.1;letter-spacing:-.5px;text-wrap:balance}
.kbox .bs{font-size:44px;line-height:1.2;margin-top:14px}
.kbox .g{background:linear-gradient(180deg,transparent 56%%,%(label)s 56%%,%(label)s 90%%,transparent 90%%);padding:0 8px;margin:0 -8px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.tiket{background:linear-gradient(160deg,#07463A,#04291F);border-radius:30px;padding:66px 50px 0;color:#fff;
 -webkit-mask:radial-gradient(circle 24px at left calc(100%% - 122px),#0000 97%%,#000),radial-gradient(circle 24px at right calc(100%% - 122px),#0000 97%%,#000);-webkit-mask-composite:source-in;mask-composite:intersect;filter:drop-shadow(0 16px 30px rgba(0,0,0,.35))}
.tiket .g{color:#7AEBD6}
.tiket .perf{margin:30px -26px 0;border-top:3px dashed rgba(255,255,255,.28)}
.tiket .bs{color:rgba(255,255,255,.9);margin:0;height:119px;display:flex;align-items:center;justify-content:space-between;gap:20px;font-size:34px;white-space:nowrap}
.tiket .bs .ik{flex:none;width:58px;opacity:.9}
.neo{background:#AAFFEF;border:4px solid #111;border-radius:24px;box-shadow:12px 12px 0 #111;padding:64px 46px 42px;color:#111}
.neo .g{color:#04503F}
.neo .bs{color:#111}
.strp{transform:rotate(-2deg);transform-origin:left bottom;padding-left:6px;margin-top:40px}
.kbox.k-strip .kick{top:-30px}
.strp .bj{line-height:1.32}
.strp .bj .ln{background:#05362C;color:#fff;padding:2px 22px 8px;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.strp .g{color:#7AEBD6}
.strp .bs{margin-top:22px}
.strp .bs span{background:#fff;color:#111;padding:6px 18px;font-size:38px;box-decoration-break:clone;-webkit-box-decoration-break:clone;line-height:1.5}
/* ---- headline tipografi: lingkar, editorial, poster ---- */
.tshade{position:absolute;left:0;right:0;top:0;height:62%%;z-index:1;background:linear-gradient(180deg,rgba(3,30,25,.88) 0%%,rgba(3,30,25,.62) 45%%,rgba(3,30,25,0) 100%%)}
.tipo{position:absolute;z-index:2;left:60px;right:60px;color:#fff;text-align:center}
.tipo .g{position:relative;display:inline-block}
.lingkar{top:180px}
.lingkar .l{font-family:HeadFont,sans-serif;font-size:96px;line-height:1.06;letter-spacing:-1.5px;text-wrap:balance}
.lingkar .g{color:#fff;padding:0 6px}
.lingkar .g svg{position:absolute;left:-26px;right:-26px;top:-14px;bottom:-18px;width:calc(100%% + 52px);height:calc(100%% + 32px);overflow:visible}
.lingkar .s{font-size:34px;margin-top:26px;opacity:.92}
.ajak{position:absolute;z-index:3;left:50%%;transform:translateX(-50%%);bottom:118px;display:flex;align-items:center;gap:22px;white-space:nowrap;padding:10px 10px 10px 34px;border-radius:44px;color:#fff;font-size:32px;font-weight:500;
 background:rgba(255,255,255,.14);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1.5px solid rgba(255,255,255,.45)}
.ajak .ar{width:74px;height:56px;border-radius:16px;background:#AAFFEF;display:flex;align-items:center;justify-content:center}
.editorial{bottom:120px}
.editorial .e1{font-family:HeadFont,sans-serif;font-size:42px;letter-spacing:.5px}
.editorial .e2{font-family:SeakunSerif,Georgia,serif;font-style:normal;font-size:150px;line-height:.95;letter-spacing:-2px;color:#F6EFE6}
.editorial .g{font-family:HeadFont,sans-serif;font-size:96px;letter-spacing:-1px;color:#fff;background:%(label)s;padding:0 22px 6px;transform:rotate(-2deg);margin:8px 0;line-height:1.15}
.editorial .s{font-size:30px;letter-spacing:2px;margin-top:26px;opacity:.9}
.poster{top:168px;text-align:left}
.poster .p{font-family:SeakunPoster,Impact,sans-serif;white-space:nowrap;font-size:168px;line-height:.92;text-transform:uppercase;letter-spacing:1px}
.poster .g{color:#7AEBD6}
.torn{display:inline-block;background:%(label)s;color:#fff;font-weight:700;text-transform:uppercase;font-size:34px;letter-spacing:1px;padding:14px 26px;clip-path:polygon(0%% 2.9%%,4%% 1.4%%,8%% 5.9%%,12%% 0.7%%,16%% 4.8%%,20%% 3.3%%,24%% 0.5%%,28%% 4.6%%,32%% 0.3%%,36%% 3.9%%,40%% 0.6%%,44%% 0.8%%,48%% 3.8%%,52%% 7.4%%,56%% 1.1%%,60%% 2.0%%,64%% 5.6%%,68%% 8.5%%,72%% 5.2%%,76%% 3.6%%,80%% 8.8%%,84%% 0.4%%,88%% 7.7%%,92%% 2.6%%,96%% 1.3%%,100%% 1.1%%,100%% 97.2%%,96%% 92.7%%,92%% 98.4%%,88%% 94.8%%,84%% 94.2%%,80%% 96.6%%,76%% 95.1%%,72%% 99.4%%,68%% 99.5%%,64%% 98.1%%,60%% 93.9%%,56%% 96.2%%,52%% 97.2%%,48%% 94.7%%,44%% 95.9%%,40%% 97.3%%,36%% 92.9%%,32%% 93.7%%,28%% 97.8%%,24%% 94.8%%,20%% 95.3%%,16%% 92.1%%,12%% 93.4%%,8%% 97.4%%,4%% 91.2%%,0%% 98.9%%)}
.torn.t1{transform:rotate(-2deg);margin-bottom:6px}
.torn.t2{background:#fff;color:#111;font-weight:600;text-transform:none;font-size:36px;transform:rotate(1.5deg);margin-top:16px}
/* ---- slide data & CTA (format "cerita di balik") ---- */
.dt{position:absolute;z-index:2;left:72px;right:72px;top:168px;bottom:118px;display:flex;flex-direction:column}
.dt .lb{display:flex;justify-content:space-between;font-weight:600;font-size:19px;letter-spacing:3px;text-transform:uppercase;color:#7a7a7a}
.dt .lb b{color:%(pink)s}
.dt .jd{font-family:HeadFont,sans-serif;font-size:66px;line-height:1.08;letter-spacing:-1px;color:#111;margin-top:4px;text-wrap:balance}
.dt .jd .g{background:#FFE38A;color:#17201D;border-radius:999px;padding:0 .28em;margin:0 .02em;box-decoration-break:clone;-webkit-box-decoration-break:clone;position:relative;display:inline-block;line-height:1.12}
.dt .gb{border-radius:30px;overflow:hidden;margin:0 0 30px;box-shadow:0 14px 34px rgba(0,0,0,.14);flex:none}
.dt .gb img{width:100%%;height:100%%;object-fit:cover;display:block}
.dt .jd .g:last-of-type::after{content:'';position:absolute;right:-.55em;top:-.45em;width:.6em;height:.6em;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><g stroke='%%23FFC233' stroke-width='5' stroke-linecap='round'><path d='M8 30 L16 18'/><path d='M20 26 L33 20'/><path d='M14 12 L18 3'/></g></svg>") no-repeat center/contain}
.dt .is p{font-size:29px;line-height:1.45;color:#3a3a3a;margin-top:18px;text-wrap:pretty}
.dt .is b,.dt .is .pk{color:#111;font-weight:700}
.dt .is .tl{background:#0B8F72;color:#fff;font-weight:700;border-radius:999px;padding:1px .45em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.dt .is .hl{background:#CDEFE6;color:#0B3D33;font-weight:700;border-radius:999px;padding:1px .45em}
.dt .vz{margin-top:30px;flex:1;display:flex;flex-direction:column;justify-content:center}
.dt .pt{margin-top:auto;font-family:HeadFont,sans-serif;font-size:36px;line-height:1.2;color:#111;text-wrap:balance;padding-top:24px}
.dt .pt .g{background:#FFE38A;color:#17201D;border-radius:999px;padding:0 .28em;margin:0 .02em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.dt .sb{font-size:15px;color:#8a8a8a;margin-top:12px;line-height:1.35}
.vz .ab{font-family:HeadFont,sans-serif;font-size:190px;line-height:1.05;letter-spacing:-6px;color:%(pink)s}
.vz .ab.o{color:%(label)s}
.vz .ak{font-size:27px;color:#444;margin-top:34px}
.vz .ab2{display:flex;gap:28px}
.vz .ab2 > div{flex:1;border-radius:30px;padding:40px 34px;background:rgba(255,255,255,.65);border:2px solid rgba(0,0,0,.06)}
.vz .ab2 .n{font-family:HeadFont,sans-serif;font-size:120px;line-height:1.12;letter-spacing:-3px}
.vz .ab2 .k{font-size:24px;color:#555;margin-top:8px}
.vz .br{display:flex;align-items:center;gap:18px;margin:20px 0}
.vz .br .l{width:130px;font-weight:600;font-size:25px;color:#444;flex:none}
.vz .br .t{flex:1;height:76px;border-radius:14px;background:rgba(0,0,0,.05);position:relative}
.vz .br .f{height:100%%;border-radius:14px;background:#BFE6DC;display:flex;align-items:center;justify-content:flex-end;padding-right:16px;font-weight:700;font-size:25px;color:#0b4a3d;min-width:150px}
.vz .br.s .f{background:%(hj)s;color:#fff}
.vz .br.o .f{background:%(or)s;color:#fff}
.vz .bj{font-size:21px;color:#777;margin-bottom:6px;letter-spacing:1px;text-transform:uppercase;font-weight:600}
.vz .dvs{display:flex;gap:24px}
.vz .dvs > div{flex:1;border-radius:26px;padding:26px 28px}
.vz .dvs .a{background:#E7E4DF}
.vz .dvs .b{background:%(pink)s;color:#fff}
.vz .dvs h4{font-size:20px;letter-spacing:3px;font-weight:700;margin-bottom:14px;opacity:.8}
.vz .dvs li{list-style:none;font-size:27px;line-height:1.3;margin:10px 0;font-weight:500}
.vz .tb{width:100%%;border-collapse:collapse;font-size:29px}
.vz .tb th{font-size:18px;letter-spacing:2.5px;text-transform:uppercase;color:#888;text-align:left;padding:0 10px 12px;font-weight:700}
.vz .tb th.s,.vz .tb td.s{color:%(pink)s}
.vz .tb td{padding:22px 10px;border-top:2px solid rgba(0,0,0,.08);line-height:1.25;font-weight:500;color:#222}
.vz .tb td:first-child{color:#777;font-weight:600;font-size:20px;letter-spacing:1px;text-transform:uppercase;width:24%%}
.vz .tb td.s{font-weight:700}
.vz .ds li{list-style:none;display:flex;gap:16px;align-items:flex-start;font-size:28px;line-height:1.35;margin:14px 0;color:#222}
.vz .ds li i{flex:none;width:40px;height:40px;border-radius:12px;background:%(pink)s;color:#fff;font-style:normal;font-weight:700;font-size:22px;display:flex;align-items:center;justify-content:center;margin-top:2px}
.vz .kt{border-left:8px solid %(label)s;padding:8px 0 8px 28px;font-family:HeadFont,sans-serif;font-size:46px;line-height:1.2;color:#111}
.vz .kt small{display:block;font-family:BodyFont,sans-serif;font-size:22px;color:#777;margin-top:12px;font-weight:500}
.hp{margin:6px auto 0;width:640px;border-radius:46px;background:#111;padding:26px 22px 30px;box-shadow:0 24px 50px rgba(0,0,0,.25)}
.hp .jam{color:#fff;text-align:center;font-family:HeadFont,sans-serif;font-size:58px;margin-bottom:14px}
.hp .nt{background:rgba(255,255,255,.93);border-radius:22px;padding:14px 20px;margin:10px 0;display:flex;justify-content:space-between;align-items:center;gap:14px}
.hp .nt .ap{font-size:16px;color:#777;font-weight:600;letter-spacing:.5px}
.hp .nt .tx{font-size:23px;color:#111;font-weight:600;line-height:1.25}
.hp .nt .rp{font-weight:700;font-size:25px;white-space:nowrap}
.hp .nt .rp.p{color:%(pink)s}.hp .nt .rp.m{color:%(label)s}
.hp .nt.akhir{background:%(label)s}.hp .nt.akhir .tx,.hp .nt.akhir .ap,.hp .nt.akhir .rp{color:#fff}
.cta2{position:absolute;z-index:2;left:72px;right:72px;top:190px;bottom:118px;display:flex;flex-direction:column;color:#fff}
.cta2 .jb{font-family:HeadFont,sans-serif;font-size:68px;line-height:1.1;letter-spacing:-1px;text-wrap:balance}
.cta2 .jb .g{background:#FFE38A;color:#17201D;border-radius:999px;padding:0 .28em;margin:0 .02em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.cta2 .mf{font-size:30px;line-height:1.45;margin-top:22px;opacity:.92}
.cta2 .gr{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:34px}
.cta2 .gr div{border-radius:24px;padding:22px 20px;background:rgba(255,255,255,.10);border:1.5px solid rgba(255,255,255,.28);display:flex;align-items:center;gap:14px;font-weight:600;font-size:24px}
.cta2 .gr i{flex:none;width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:HeadFont,sans-serif;font-size:24px;color:#fff}
.cta2 .gb{border-radius:30px;overflow:hidden;margin-top:34px;flex:none;box-shadow:0 14px 34px rgba(0,0,0,.3)}
.cta2 .gb img{width:100%%;height:100%%;object-fit:cover;display:block}
.cta2 .bt{margin-top:auto;align-self:flex-start;display:flex;align-items:center;gap:18px;background:#AAFFEF;color:#06352C;border-radius:60px;padding:16px 18px 16px 38px;font-weight:700;font-size:34px}
.cta2 .bt span{background:#06352C;color:#fff;border-radius:40px;padding:10px 26px;font-size:30px}
.cta2 .ss{font-size:22px;opacity:.75;margin-top:18px}
/* ---- variasi gambar & komponen sorotan (revisi user 20 Nov) ---- */
.dt.m-pojok .jd,.dt.m-pojok .is{padding-right:330px}
.gpo{position:absolute;top:-6px;right:-6px;width:300px;background:#fff;padding:14px 14px 46px;box-shadow:0 18px 36px rgba(0,0,0,.18);z-index:3}
.gpo img{width:100%%;height:290px;object-fit:cover;display:block}
.gpo span{position:absolute;left:0;right:0;bottom:10px;text-align:center;font-size:19px;font-weight:600;color:#555}
.gli{position:absolute;top:0;right:0;width:290px;height:290px;border-radius:50%%;overflow:hidden;border:10px solid #fff;box-shadow:0 0 0 6px %(or)s,0 18px 36px rgba(0,0,0,.18)}
.gli img{width:100%%;height:100%%;object-fit:cover}
.sisi{display:flex;gap:30px;align-items:stretch}
.sisi .tx{flex:1.6}.sisi .gsi{flex:1;border-radius:30px;overflow:hidden;box-shadow:0 14px 34px rgba(0,0,0,.16)}
.sisi .gsi img{width:100%%;height:100%%;object-fit:cover}
.gst{display:flex;gap:18px;margin-top:26px}
.gst > div{flex:1;height:200px;border-radius:22px;overflow:hidden;border:6px solid #fff;box-shadow:0 10px 24px rgba(0,0,0,.15);position:relative}
.gst span{position:absolute;left:8px;bottom:8px;background:#fff;color:#17201D;font-weight:700;font-size:18px;border-radius:10px;padding:3px 10px}
.gst img{width:100%%;height:100%%;object-fit:cover}
.vs{display:flex;align-items:stretch;position:relative}
.vs .c{flex:1;border-radius:32px;padding:34px 30px 30px;position:relative}
.vs .c.a{background:#fff;border:3px solid %(ink)s;color:%(ink)s}
.vs .c.b{background:%(hj)s;color:#fff;margin-left:120px}
.vs .lb{font-weight:700;font-size:22px;letter-spacing:3px;opacity:.7}
.vs .n{font-family:HeadFont,sans-serif;font-size:76px;white-space:nowrap;line-height:1.1;letter-spacing:-2px;margin-top:8px}
.vs .k{font-size:22px;opacity:.8;margin-top:6px}
.vs .ar{position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);width:112px;height:112px;border-radius:50%%;background:%(or)s;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:HeadFont,sans-serif;font-size:30px;box-shadow:0 0 0 10px #F1F2F3,0 14px 30px rgba(255,122,26,.45);z-index:2;line-height:1}
.vs .ar svg{margin-bottom:4px}
.vs-cat{margin-top:24px;display:inline-block;font-size:24px;font-weight:600;color:%(ink)s;background:%(kn)s;border-radius:40px;padding:10px 24px}
.bl{position:relative;padding-top:50px}
.bl .rw{display:flex;align-items:center;gap:18px;margin:18px 0}
.bl .lb{width:150px;font-weight:700;font-size:25px;color:%(ink)s;flex:none}
.bl .tr{flex:1;position:relative;height:84px}
.bl .f{height:100%%;border-radius:0 42px 42px 0;display:flex;align-items:center;justify-content:flex-end;padding-right:22px;font-family:HeadFont,sans-serif;font-size:38px;min-width:170px}
.bl .gr{position:absolute;top:-50px;bottom:-14px;border-left:4px dashed %(ink)s;z-index:2}
.bl .gr span{position:absolute;top:0;left:10px;white-space:nowrap;font-size:20px;font-weight:700;color:%(ink)s;background:%(kn)s;border-radius:20px;padding:4px 14px}
.vz .an{display:flex;justify-content:flex-end;align-items:center;gap:12px;margin-top:10px;font-family:HeadFont,sans-serif;font-size:34px;color:%(or)s}
.tn{display:flex;align-items:center;gap:34px}
.tn .ic{flex:none;width:190px;height:190px;border-radius:50%%;background:%(or)s;display:flex;align-items:center;justify-content:center;box-shadow:0 18px 40px rgba(255,122,26,.4)}
.tn .n{font-family:HeadFont,sans-serif;font-size:170px;line-height:1.05;letter-spacing:-6px;color:%(ink)s}
.tn .k{font-size:26px;color:#444;margin-top:8px;max-width:600px}
.tn-ch{display:flex;gap:16px;margin-top:30px}
.tn-ch div{flex:1;border-radius:24px;padding:20px 24px;background:#fff;border:3px solid %(ink)s;display:flex;align-items:center;gap:18px}
.tn-ch > div > b{font-family:HeadFont,sans-serif;font-size:52px;color:%(or)s;font-weight:400}
.tn-ch span{font-size:22px;color:#333;line-height:1.3}
.glt{position:absolute;left:0;top:0;width:100%%;object-fit:cover;z-index:1;border-radius:0 0 56px 56px}
.glt-v{position:absolute;left:0;top:0;width:100%%;z-index:1;border-radius:0 0 56px 56px;background:linear-gradient(180deg,rgba(0,0,0,.35) 0%%,rgba(0,0,0,0) 30%%,rgba(10,20,17,.55) 62%%,rgba(10,20,17,.8) 100%%)}
.dt.m-latar .jd{color:#fff;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.dt.m-latar .is p{color:rgba(255,255,255,.92)}
.dt.m-latar .is b,.dt.m-latar .is .pk{color:#fff}
.dt.m-latar .vz{margin-top:56px}
.bisi{position:absolute;z-index:2;left:64px;right:64px}
.bisi p{font-size:31px;line-height:1.5;color:#151515;margin-bottom:32px;text-wrap:pretty}
.bisi b,.bisi .pk{font-weight:700;color:#111}
.bisi .g{color:%(pink)s;font-weight:700}
.bar{position:absolute;z-index:3;left:56px;right:56px;bottom:34px;height:46px;border-radius:24px;color:#0B3D33;display:flex;align-items:center;justify-content:space-between;padding:0 22px;
 background:linear-gradient(120deg,rgba(8,160,129,.55),rgba(74,209,185,.30));backdrop-filter:blur(16px) saturate(160%%);-webkit-backdrop-filter:blur(16px) saturate(160%%);
 border:1.5px solid rgba(255,255,255,.45);box-shadow:0 8px 26px rgba(0,0,0,.18),inset 0 1px 0 rgba(255,255,255,.35)}
.bar.padat{background:linear-gradient(120deg,rgba(255,255,255,.95),rgba(255,255,255,.66));border-color:rgba(255,255,255,1);box-shadow:0 10px 26px rgba(0,0,0,.10),inset 0 1px 0 #fff}
.bar .a{font-weight:700;font-size:20px;color:#0B5C4B}
.bar .m{font-size:15px;font-weight:500;letter-spacing:.6px;opacity:.95;display:flex;align-items:center;gap:10px}
.bar .m.sm{font-size:14px;letter-spacing:.2px;max-width:640px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;display:block;opacity:.92}
.bar .m i{width:5px;height:5px;border-radius:50%%;background:#0B3D33;opacity:.6}
.bar .z{display:flex;align-items:center;gap:8px;font-weight:600;font-size:18px}
.bar .z .c{width:28px;height:28px;border-radius:50%%;background:#0B5C4B;border:none;display:flex;align-items:center;justify-content:center}
.kjg .w{background:%(pink)s;color:#fff;font-weight:700;font-size:30px;border-radius:50px;padding:12px 34px}
"""

def fontfaces():
    fd = "file://" + os.path.join(HERE, "font")
    f = BRAND["fonts"]
    out = [f"@font-face{{font-family:HeadFont;src:url('{fd}/{f['heading']}')}}"]
    if len(set(f["body"].values())) == 1 and "Variable" in next(iter(f["body"].values())):
        out.append(f"@font-face{{font-family:BodyFont;font-weight:100 900;src:url('{fd}/{next(iter(f['body'].values()))}')}}")
    else:
        for w, fn in f["body"].items():
            out.append(f"@font-face{{font-family:BodyFont;font-weight:{w};src:url('{fd}/{fn}')}}")
    for fam, fn in BRAND.get("fonts_extra", {}).items():
        out.append(f"@font-face{{font-family:{fam};src:url('{fd}/{fn}')}}")
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

def vis_html(v):
    """Visual data untuk layout "data". v = {"tipe": ..., ...}."""
    if not v:
        return ""
    t = v.get("tipe")
    e = lambda x: html.escape(str(x))
    if t == "versus":
        a, b = v["kiri"], v["kanan"]
        arrow = '<svg width="44" height="30" viewBox="0 0 44 30" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 15h36M28 4l11 11-11 11"/></svg>'
        card = lambda c, k: f'<div class="c {k}"><div class="lb">{e(c.get("label", ""))}</div><div class="n">{e(c["angka"])}</div><div class="k">{md(c.get("ket", ""))}</div></div>'
        cat = f'<div class="vs-cat">{md(v["catatan"])}</div>' if v.get("catatan") else ""
        return f'<div class="vs">{card(a, "a")}<div class="ar">{arrow}{e(v.get("badge", ""))}</div>{card(b, "b")}</div>{cat}'
    if t == "balapan":
        mx = max(float(i["nilai"]) for i in v["items"]) or 1
        warna = {"hijau": C["hj"], "oranye": C["or"], "kuning": C["kn"], "gelap": C["ink"]}
        rows = ""
        for k, i in enumerate(v["items"]):
            w = float(i["nilai"]) / mx * 100
            col = warna.get(i.get("warna", "hijau"), C["hj"])
            tc = "#17201D" if i.get("warna") == "kuning" else "#fff"
            gr = ""
            if k == 0 and v.get("garis"):
                pos = float(v["garis"]["nilai"]) / mx * 100
                gr = f'<div class="gr" style="left:{pos:.1f}%"><span>{e(v["garis"]["teks"])}</span></div>'
            rows += (f'<div class="rw"><div class="lb">{e(i["label"])}</div><div class="tr">{gr}'
                     f'<div class="f" style="width:{max(22, w):.1f}%;background:{col};color:{tc}">{e(i.get("teks", i["nilai"]))}</div></div></div>')
        an = ""
        if v.get("anotasi"):
            up = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>'
            an = f'<div class="an">{up}{md(v["anotasi"])}</div>'
        return f'<div class="bl">{rows}</div>{an}'
    if t == "turun":
        down = '<svg width="110" height="110" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v15M5 12l7 7 7-7"/></svg>'
        ch = "".join(f'<div><b>{e(c["angka"])}</b><span>{md(c.get("ket", ""))}</span></div>' for c in v.get("pendamping", []))
        return (f'<div class="tn"><div class="ic">{down}</div><div><div class="n">{e(v["angka"])}</div><div class="k">{md(v.get("ket", ""))}</div></div></div>'
                + (f'<div class="tn-ch">{ch}</div>' if ch else ""))
    if t == "angka-besar":
        if v.get("pembanding"):
            cells = "".join(f'<div><div class="n" style="color:{C["label"] if p.get("warna") == "oranye" else C["pink"]}">{e(p["angka"])}</div><div class="k">{md(p.get("ket", ""))}</div></div>' for p in v["pembanding"])
            return f'<div class="ab2">{cells}</div>'
        return f'<div class="ab{" o" if v.get("warna") == "oranye" else ""}">{e(v["angka"])}</div><div class="ak">{md(v.get("ket", ""))}</div>'
    if t == "batang":
        mx = max(float(i["nilai"]) for i in v["items"]) or 1
        rows = "".join(f'<div class="br{" s" if i.get("sorot") == True or i.get("sorot") == "hijau" else (" o" if i.get("sorot") == "oranye" else "")}"><div class="l">{e(i["label"])}</div>'
                       f'<div class="t"><div class="f" style="width:{max(18, float(i["nilai"]) / mx * 100):.1f}%">{e(i.get("teks", i["nilai"]))}</div></div></div>' for i in v["items"])
        return (f'<div class="bj">{e(v["judul"])}</div>' if v.get("judul") else "") + rows
    if t == "dulu-vs-sekarang":
        a, b = v.get("kiri", {}), v.get("kanan", {})
        li = lambda xs: "".join(f"<li>{md(x)}</li>" for x in xs)
        return (f'<div class="dvs"><div class="a"><h4>{e(a.get("judul", "DULU"))}</h4><ul>{li(a.get("isi", []))}</ul></div>'
                f'<div class="b"><h4>{e(b.get("judul", "SEKARANG"))}</h4><ul>{li(b.get("isi", []))}</ul></div></div>')
    if t == "tabel":
        k = v["kolom"]; sc = v.get("sorot_kolom", len(k) - 1)
        th = "".join(f'<th class="{"s" if i == sc else ""}">{e(c)}</th>' for i, c in enumerate(k))
        tr = "".join("<tr>" + "".join(f'<td class="{"s" if i == sc else ""}">{md(str(c))}</td>' for i, c in enumerate(r)) + "</tr>" for r in v["baris"])
        return f'<table class="tb"><tr>{th}</tr>{tr}</table>'
    if t == "daftar":
        return '<ul class="ds">' + "".join(f'<li><i>{k + 1}</i><span>{md(x)}</span></li>' for k, x in enumerate(v["items"])) + "</ul>"
    if t == "kutipan":
        return f'<div class="kt">{md(v["teks"])}' + (f'<small>{e(v["oleh"])}</small>' if v.get("oleh") else "") + "</div>"
    if t == "notif":
        rows = ""
        for n in v["items"]:
            cls = " akhir" if n.get("akhir") else ""
            rp = n.get("rp", "")
            rows += (f'<div class="nt{cls}"><div><div class="ap">{e(n.get("app", ""))}</div><div class="tx">{md(n.get("teks", ""))}</div></div>'
                     + (f'<div class="rp {"p" if rp.startswith("+") else "m"}">{e(rp)}</div>' if rp else "") + "</div>")
        return f'<div class="hp"><div class="jam">{e(v.get("jam", "09.41"))}</div>{rows}</div>'
    return ""

def slide_html(s, n=1):
    layout = s.get("layout", "kiri")
    bg = BG.get(s.get("bg", BG_DEFAULT), BG[BG_DEFAULT])
    veil = s.get("veil", {"kiri": "kiri", "tengah": "atas", "threads": "none", "foto-atas": "none", "data": "none", "cta-seakun": "none", "berita-isi": "none"}.get(layout, "kiri"))
    vstop = s.get("veil_until", 62 if veil == "kiri" else 55)
    vcss = {"kiri": f"linear-gradient(90deg,{bg} 0%,{bg}EE 38%,{bg}00 62%)",
            "atas": f"linear-gradient(180deg,{bg} 0%,{bg}F0 {vstop-21}%,{bg}00 {vstop}%)",
            "none": "none"}[veil]
    tex = BRAND.get("texture") if s.get("texture", layout != "cta-seakun") else None
    if layout == "cta-seakun":
        bg = s.get("bg_warna", "linear-gradient(160deg,#07463A,#04291F)")
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
    berita = layout in ("berita", "berita-isi", "data", "cta-seakun")
    if berita and s.get("foto"):
        fh = s.get("foto_height", H if layout == "berita" else 700)
        out.append(f'<img class="bfoto" src="{uri(s["foto"])}" style="height:{fh}px;object-position:{s.get("foto_pos", "center center")}">')
        out.append('<div class="bshade"></div>')
    if berita and s.get("header", True):
        terang = bool(s.get("foto")) or layout == "cta-seakun" or (layout == "data" and s.get("gambar_mode") == "latar" and s.get("gambar"))
        out.append(f'<div class="hdr3{"" if terang else " gelap"}"><img src="{uri(BRAND["logo_footer"] if terang else BRAND["logo_header"])}">'
                   f'<div class="tg"><i></i>{html.escape(BRAND.get("tagline_pendek", "Platform Patungan No.1 Indonesia"))}<i></i></div></div>')
    elif s.get("header", True) and BRAND.get("header_style") == "seakun":
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
    elif layout not in ("foto-atas", "berita", "berita-isi", "data", "cta-seakun"):
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
    if layout == "berita":
        gaya = s.get("kartu", BRAND.get("kartu_default", "klasik"))
        sub = f'<div class="bs">{green(s["subjudul"])}</div>' if s.get("subjudul") else ""
        jdl = f'<div class="bj">{green(s.get("judul", ""))}</div>'
        top = s.get("text_top", 560)
        wm = f'<img class="wm" src="{uri(BRAND.get("logo_ikon", BRAND["logo_header"]))}">'
        if gaya in ("lingkar", "editorial", "poster"):
            lines = s.get("judul", "").split("\n")
            def hk(t, svg=False):
                h = html.escape(curly(t), quote=False)
                ring = ('<svg viewBox="0 0 200 100" preserveAspectRatio="none"><path d="M 18,62 C 4,22 120,2 186,30 C 214,48 170,92 96,94 C 30,96 0,70 22,36 C 40,14 110,8 150,14" '
                        'fill="none" stroke="#FF4F2F" stroke-width="5" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>') if svg else ""
                return re.sub(r"__([\s\S]+?)__", lambda m: f'<span class="g">{m.group(1)}{ring}</span>', h)
            sub = html.escape(s.get("subjudul", ""))
            if gaya == "lingkar":
                out.append('<div class="tshade"></div>')
                body = "".join(f'<div class="l">{hk(l, True)}</div>' for l in lines)
                out.append(f'<div class="tipo lingkar">{body}' + (f'<div class="s">{sub}</div>' if sub else "") + "</div>")
                if s.get("ajakan"):  # tombol ajakan opsional (default: tidak ada)
                    out.append(f'<div class="ajak">{html.escape(s["ajakan"])}<span class="ar">{icon("chevron-right",30,"#111",2.6)}</span></div>')
            elif gaya == "editorial":
                out.append('<div class="tgrad" style="height:80%"></div>')
                body = f'<div class="e1">{hk(lines[0])}</div>' + "".join(
                    (f'<div>{hk(l)}</div>' if "__" in l else f'<div class="e2">{hk(l)}</div>') for l in lines[1:])
                out.append(f'<div class="tipo editorial">{body}' + (f'<div class="s">{sub}</div>' if sub else "") + "</div>")
            else:
                out.append('<div class="tshade" style="height:78%"></div>')
                kick = f'<div class="torn t1">{html.escape(s["kicker"])}</div>' if s.get("kicker") else ""
                body = "".join(f'<div class="p">{hk(l)}</div>' for l in lines)
                out.append(f'<div class="tipo poster">{kick}{body}' + (f'<div class="torn t2">{sub}</div>' if sub else "") + "</div>")
        elif gaya in ("tiket", "neo", "strip"):
            kick = f'<div class="kick">{icon("star",20,"#fff",2.6)}{html.escape(s["kicker"])}</div>' if s.get("kicker") else ""
            judul = green(s.get("judul", ""))
            subj = green(s.get("subjudul", "")) if s.get("subjudul") else ""
            if gaya == "tiket":
                ik = f'<img class="ik" src="{uri(BRAND["logo_footer"])}" style="width:128px">'
                inner = f'<div class="tiket"><div class="bj">{judul}</div><div class="perf"></div><div class="bs"><span>{subj}</span>{ik}</div></div>'
            elif gaya == "neo":
                inner = f'<div class="neo"><div class="bj">{judul}</div>' + (f'<div class="bs">{subj}</div>' if subj else "") + "</div>"
            else:
                inner = (f'<div class="strp"><div class="bj"><span class="ln">{judul}</span></div>'
                         + (f'<div class="bs"><span>{subj}</span></div>' if subj else "") + "</div>")
            out.append(f'<div class="kbox k-{gaya}">{kick}{inner}</div>')
        elif gaya in ("gradasi", "kaca"):
            kick = f'<div class="kick">{icon("star",20,"#fff",2.6)}{html.escape(s["kicker"])}</div>' if s.get("kicker") else ""
            if gaya == "gradasi":
                out.append('<div class="tgrad"></div>')
            ln = '<div class="ln"></div>' if gaya == "gradasi" else ""
            out.append(f'<div class="kartu {gaya}">{kick}{jdl}{sub}{ln}</div>')
        elif gaya == "stiker":
            kick = f'<div class="kick">{icon("star",20,"#fff",2.6)}{html.escape(s["kicker"])}</div>' if s.get("kicker") else ""
            out.append(f'<div class="kartu stiker" style="top:{top}px">{kick}{jdl}{sub}{wm}</div>')
        elif gaya == "pita":
            kk = f'<span class="kk"><i></i>{html.escape(s.get("kicker", ""))}</span>'
            out.append(f'<div class="kartu pita" style="top:{top}px"><div class="pt">{kk}<span class="dd"><i></i><i></i><i></i></span></div>'
                       f'<div class="bd">{jdl}{sub}</div></div>')
        else:
            strip = "".join(f'<i style="background:{c}"></i>' for c in BRAND.get("dots", [C["pink"]])[:3])
            kick = f'<div class="kick">{html.escape(s["kicker"])}</div>' if s.get("kicker") else ""
            out.append(f'<div class="kartu" style="top:{top}px"><div class="strip">{strip}</div>{kick}{jdl}{sub}</div>')
    if layout == "berita-isi":
        paras = "".join(f"<p>{md(p).replace('class="tl"', 'class="g"')}</p>" for p in s.get("body", []))
        out.append(f'<div class="bisi" style="top:{s.get("text_top", 770)}px">{paras}</div>')
    if layout == "data":
        def jdl(t):
            return green(t)
        lb = s.get("label", "")
        hal = s.get("halaman", "")
        vz = vis_html(s.get("visual"))
        isi = "".join(f"<p>{md(p)}</p>" for p in s.get("isi", []))
        mode = s.get("gambar_mode", "atas")
        gl = s.get("gambar") if isinstance(s.get("gambar"), list) else ([s["gambar"]] if s.get("gambar") else [])
        img = lambda g: f'<img src="{uri(g)}" style="object-position:{s.get("gambar_pos", "center")}">'
        gb, kelas, body_top = "", "", 0
        if gl and mode == "atas":
            gb = f'<div class="gb" style="height:{s.get("gambar_tinggi", 430)}px">{img(gl[0])}</div>'
        elif gl and mode == "polaroid":
            gb = f'<div class="gpo" style="transform:rotate({s.get("gambar_miring", 4)}deg)">{img(gl[0])}<span>{html.escape(s.get("gambar_ket", ""))}</span></div>'; kelas = " m-pojok"
        elif gl and mode == "lingkaran":
            gb = f'<div class="gli">{img(gl[0])}</div>'; kelas = " m-pojok"
        elif gl and mode == "strip":
            labs = s.get("gambar_label", [])
            gb = '<div class="gst">' + "".join(f'<div style="transform:rotate({r}deg)">{img(g)}' + (f'<span>{html.escape(labs[k])}</span>' if k < len(labs) else "") + '</div>'
                                              for k, (g, r) in enumerate(zip(gl, [-3, 2, -1.5, 3, -2]))) + "</div>"
        head = (f'<div class="jd" style="font-size:{s.get("judul_size", 66)}px">{jdl(s.get("judul", ""))}</div>'
                + (f'<div class="is">{isi}</div>' if isi else ""))
        if gl and mode == "latar":
            out.append(f'<img class="glt" src="{uri(gl[0])}" style="height:{s.get("gambar_tinggi", 640)}px;object-position:{s.get("gambar_pos", "center")}">'
                       f'<div class="glt-v" style="height:{s.get("gambar_tinggi", 640)}px"></div>')
            kelas = " m-latar"
            body_top = s.get("gambar_tinggi", 640) - 250
        if gl and mode == "sisi":
            head = f'<div class="sisi"><div class="tx">{head}</div><div class="gsi" style="height:{s.get("gambar_tinggi", 420)}px">{img(gl[0])}</div></div>'
            gb = ""
        if mode == "strip":
            body = head + gb
        else:
            body = (gb if mode == "atas" else "") + head + (gb if mode in ("polaroid", "lingkaran") else "")
        gaya_dt = f' style="top:{body_top}px"' if mode == "latar" and gl else ""
        out.append(f'<div class="dt{kelas}"{gaya_dt}>{body}' + (f'<div class="vz">{vz}</div>' if vz else "")
                   + (f'<div class="pt">{green(s["penutup"])}</div>' if s.get("penutup") else "") + "</div>")
    if layout == "cta-seakun":
        warna = ["#E50914", "#1DB954", "#FF0000", "#113CCF", "#10A37F", "#7D2AE8"]
        gr = "".join(f'<div><i style="background:{warna[k % len(warna)]}">{html.escape(n[0])}</i>{html.escape(n)}</div>'
                     for k, n in enumerate(s.get("layanan", ["Netfl1x", "Sp0tify", "YouTub3", "Disn3y+", "ChatGP7", "Canv4"])))
        out.append(f'<div class="cta2"><div class="jb">{green(s.get("jembatan", ""))}</div>'
                   f'<div class="mf">{md(s.get("manfaat", "Patungan langganan premium: aman, legal, lebih hemat."))}</div>'
                   + (f'<div class="gb" style="height:{s.get("gambar_tinggi", 300)}px"><img src="{uri(s["gambar"])}" style="object-position:{s.get("gambar_pos", "center")}"></div>' if s.get("gambar") else "")
                   + f'<div class="gr">{gr}</div>'
                   f'<div class="bt">Kunjungi <span>{html.escape(BRAND["website"])}</span></div>'
                   f'<div class="ss">{html.escape(s.get("ajakan_akhir", "Simpan & bagikan ke teman yang lagi ngerasa pas-pasan juga."))}</div></div>')
    f = s.get("footer", "bar" if berita else BRAND.get("footer_default", "web-ig"))
    if f == "bar":
        padat = (not s.get("foto")) and layout != "cta-seakun"
        out.append(f'<div class="bar{" padat" if padat else ""}"><span class="a">{html.escape(BRAND["website"])}</span>'
                   + (f'<span class="m sm">Sumber: {html.escape(s["sumber"])}</span>' if s.get("sumber") else f'<span class="m">{"<i></i>".join(html.escape(x) for x in s.get("bar_tengah", BRAND.get("bar_tengah", [])))}</span>')
                   + (f'<span class="z">{icon("instagram",20,"#0B3D33",2)} @{html.escape(BRAND["handle"])}</span></div>' if s.get("bar_kanan") == "ig"
                    else f'<span class="z">{html.escape(s.get("bar_kanan", "Geser"))}<span class="c">{icon("chevron-right",18,"#fff",2.6)}</span></span></div>'))
    elif f == "kunjungi":
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
        no = s.get("nomor", i)
        hp = os.path.join(od, f"slide-{no:02d}.html")
        open(hp, "w").write(slide_html(s, s.get("nomor", i)))
        png = os.path.join(od, f"slide-{no:02d}.png")
        subprocess.run([CHROME, "--headless=new", *CHROME_EXTRA, "--disable-gpu", "--hide-scrollbars",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1",
                        f"--user-data-dir={tmp}", f"--window-size={W},{H}",
                        "--virtual-time-budget=3000", f"--screenshot={png}", "file://" + hp],
                       check=True, capture_output=True)
        print("✓", os.path.relpath(png, ROOT))
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
