#!/usr/bin/env python3
"""Cek QA otomatis visual brand. Dipakai Tilik (dan Rupa) sebelum hasil dilaporkan ke user.

Pakai:  python3 konten/brand/visual/check.py <spec.json> [--no-ill]
  --no-ill   cek teks saja (tahap prompt, sebelum ada ilustrasi)

Yang dicek per slide:
  [1] ORPHAN     1 kata sendirian di baris terakhir (judul, isi, daftar, kotak, CTA)
  [2] STABILO    stabilo kuning terpotong ke 2 baris
  [3] TEPI       teks terlalu dekat tepi slide (<60 px) / menabrak header / label footer
  [4] TABRAKAN   teks di atas area ilustrasi yang ramai (tokoh/benda), diukur dari piksel ilustrasi di bawah tiap baris
  [5] KOSONG     (catatan) area kiri di bawah teks kosong / celah besar teks-tokoh
  [7] VEIL       teks di atas tokoh yang dipudarkan veil (tokoh seperti hantu)
Tanda: ✗ = kesalahan (wajib diperbaiki), △ = catatan (Tilik menilai dari PNG).
  [6] GAYA       kata geser/swipe, 🤍, nomor judul warna aksen, sumber di slide, 2 ajakan di CTA, kutip lurus di caption
Exit code 1 kalau ada kesalahan ✗.
"""
import json, os, re, subprocess, sys, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
from PIL import Image, ImageStat

W, H = R.W, R.H
BUSY_STD = 16      # std-dev luminansi di bawah 1 baris teks; dinding polos biasanya < 8
BUSY_FRAC = 0.18   # fraksi piksel yang beda jauh dari warna dinding

JS = r"""<script>
document.fonts.ready.then(()=>{
const out=[];const blocks=document.querySelectorAll('.wrap .h, .wrap .sub, .wrap .body p, .wrap .it span, .wrap .badge .txt, .wrap .cta span, .card p');
blocks.forEach((el,bi)=>{const words=[];const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;
 while(n=walk.nextNode()){const re=/\S+/g;let m;while(m=re.exec(n.textContent)){const r=document.createRange();r.setStart(n,m.index);r.setEnd(n,m.index+m[0].length);
  const c=r.getBoundingClientRect();if(c.width>0)words.push({w:m[0],l:c.left,t:c.top,r:c.right,b:c.bottom});}}
 const lines=[];words.forEach(w=>{let L=lines.find(x=>Math.abs(x.t-w.t)<w.b-w.t-4&&Math.abs(x.b-w.b)<12);if(!L){L={t:w.t,b:w.b,l:w.l,r:w.r,words:[]};lines.push(L);}
  L.words.push(w.w);L.l=Math.min(L.l,w.l);L.r=Math.max(L.r,w.r);L.t=Math.min(L.t,w.t);L.b=Math.max(L.b,w.b);});
 lines.sort((a,b)=>a.t-b.t);
 out.push({kind:el.className||el.tagName,cls:el.closest('.h')?'h':(el.closest('.it')?'it':(el.closest('.cta')?'cta':(el.closest('.badge')?'badge':'p'))),lines:lines.map(x=>({t:x.t,b:x.b,l:x.l,r:x.r,words:x.words}))});});
const hl=[...document.querySelectorAll('.wrap .hl')].map(e=>({txt:e.textContent,n:new Set([...e.getClientRects()].map(c=>Math.round(c.top))).size}));
const rect=s=>{const e=document.querySelector(s);if(!e)return null;const c=e.getBoundingClientRect();return [c.left,c.top,c.right,c.bottom];};
const seps=[...document.querySelectorAll('.wrap .it')].filter(e=>getComputedStyle(e).borderBottomStyle!=='none'&&e.nextElementSibling).map(e=>{const c=e.getBoundingClientRect();return [c.left,c.bottom-3,c.right,c.bottom+1];});
const dots=[...document.querySelectorAll('.wrap .dot, .wrap .badge')].map(e=>{const c=e.getBoundingClientRect();return [c.left,c.top,c.right,c.bottom];});
document.getElementById('qa').textContent=JSON.stringify({blocks:out,hl:hl,ftr:rect('.ftr'),hdr:rect('.hdr'),dots:dots,seps:seps||[]});
});
</script>"""

def chrome(args, tmp):
    return subprocess.run([R.CHROME, "--headless=new", *R.CHROME_EXTRA, "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                           "--force-device-scale-factor=1", f"--user-data-dir={tmp}/u", f"--window-size={W},{H}",
                           "--virtual-time-budget=3000"] + args, capture_output=True, text=True)

def measure(s, tmp, i):
    hp = os.path.join(tmp, f"q{i}.html")
    open(hp, "w").write(R.slide_html(s).replace("</body>", '<pre id="qa" style="display:none"></pre>' + JS + "</body>"))
    r = chrome(["--dump-dom", "file://" + hp], tmp)
    m = re.search(r'<pre id="qa"[^>]*>(.*?)</pre>', r.stdout, re.S)
    import html as h
    return json.loads(h.unescape(m.group(1))) if m else None

def textless(s, tmp, i):
    """screenshot ilustrasi + veil tanpa teks/header/footer"""
    hp = os.path.join(tmp, f"bg{i}.html"); png = os.path.join(tmp, f"bg{i}.png")
    open(hp, "w").write(R.slide_html(s).replace("</head>", "<style>.wrap,.card,.hdr,.ftr{visibility:hidden!important}</style></head>"))
    chrome([f"--screenshot={png}", "file://" + hp], tmp)
    return Image.open(png).convert("RGB")

def raw_ill(s):
    p = s["illustration"]; p = p if os.path.isabs(p) else os.path.join(R.ROOT, p)
    im = Image.open(p).convert("RGB")
    # tiru object-fit:cover ke 1080x1350
    sc = max(W / im.width, H / im.height); im = im.resize((round(im.width * sc), round(im.height * sc)))
    l = (im.width - W) // 2; t = (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H))
    if s.get("flip"): im = im.transpose(Image.FLIP_LEFT_RIGHT)
    z = s.get("ill_zoom")
    if z:
        im = im.resize((round(W * z), round(H * z)))
        im = im.crop((im.width - W, im.height - H, im.width, im.height))  # jangkar kanan-bawah
    return im

def busy(img, box, wall):
    l, t, r, b = [int(v) for v in box]
    l, t = max(0, l - 4), max(0, t - 2); r, b = min(W, r + 4), min(H, b + 2)
    if r - l < 4 or b - t < 4: return 0, 0
    crop = img.crop((l, t, r, b))
    std = ImageStat.Stat(crop.convert("L")).stddev[0]
    px = crop.resize((max(1, (r - l) // 3), max(1, (b - t) // 3))).getdata()
    far = sum(1 for p in px if sum(abs(p[k] - wall[k]) for k in range(3)) > 60) / max(1, len(px))
    return std, far

def subject_top(ill):
    """baris teratas (dalam %) tempat >4% piksel berbeda dari warna dinding kiri-atas"""
    small = ill.resize((108, 135)); wall = small.crop((2, 18, 40, 40)).resize((1, 1)).getpixel((0, 0))
    for y in range(18, 135):
        row = [small.getpixel((x, y)) for x in range(108)]
        if sum(1 for p in row if sum(abs(p[k] - wall[k]) for k in range(3)) > 70) > 108 * 0.06:
            return y / 135 * 100, wall
    return 100, wall

def style_checks(s, i):
    f = []
    txt = json.dumps({k: s.get(k) for k in ("headline", "subhead", "body", "items", "badge", "cta", "threads")}, ensure_ascii=False)
    if re.search(r"\b(geser|swipe)\b", txt, re.I): f.append("GAYA: ada kata 'geser/swipe' (dilarang)")
    if "🤍" in txt: f.append("GAYA: emoji 🤍 tidak terlihat, pakai 💗")
    if re.search(r"__\s*\d+\.?\s*__", s.get("headline", "")): f.append("GAYA: nomor judul ditulis warna aksen, harus warna primer judul")
    if re.search(r"sumber\s*:", txt, re.I): f.append("GAYA: sumber ada di slide, pindahkan ke caption")
    if s.get("cta") and re.search(r"simpan", s["cta"], re.I) and re.search(r"bagikan|tag|share", s["cta"], re.I):
        f.append("GAYA: CTA berisi 2 ajakan (simpan + bagikan/tag), cukup 1")
    # Aturan user 21 Nov 2026: paragraf isi di kolom penuh tidak boleh dipenggal manual (sisa ruang kosong di kanan).
    if s.get("layout") == "data" and (not s.get("gambar") or s.get("gambar_mode", "atas") in ("atas", "latar", "strip")):
        if any("\n" in p for p in s.get("isi", [])):
            f.append("KOSONG: paragraf isi dipenggal manual (\\n) padahal kolom teks selebar slide; hapus \\n supaya paragraf penuh (full width)")
    return f

def check(spec_path, use_ill=True):
    spec = R.siapkan_spec(json.load(open(spec_path)))
    tmp = tempfile.mkdtemp(); allf = {}
    for i, s in enumerate(spec["slides"], 1):
        f = style_checks(s, i)
        s2 = dict(s) if use_ill else {k: v for k, v in s.items() if k != "illustration"}
        m = measure(s2, tmp, i)
        if not m: allf[i] = f + ["GAGAL mengukur slide"]; continue
        ftr, hdr = m["ftr"], m["hdr"]
        lines_all = []
        for blk in m["blocks"]:
            L = blk["lines"]
            if blk["cls"] == "h":
                singles = [x for x in L if len(x["words"]) == 1]
                if len(L) >= 3 and len(singles) >= 2:
                    f.append(f"ORPHAN: judul dipecah 1 kata per baris ({' / '.join(x['words'][0] for x in L)}); jadikan 1–2 baris")
            elif len(L) >= 2 and len(L[-1]["words"]) == 1 and not re.fullmatch(r"[\W\d💗❤️→]+", L[-1]["words"][0]):
                f.append(f"ORPHAN: \"{L[-1]['words'][0]}\" sendirian di baris terakhir ({' '.join(L[0]['words'][:4])}…)")
            lines_all += L
        for h in m["hl"]:
            if h["n"] > 1: f.append(f"STABILO: \"{h['txt']}\" terpotong ke {h['n']} baris")
        for L in lines_all:
            if L["l"] < 56 or L["r"] > W - 56: f.append(f"TEPI: baris \"{' '.join(L['words'][:4])}…\" terlalu dekat tepi")
            for nm, bx in (("label footer", ftr), ("header", hdr)):
                if bx and L["r"] > bx[0] and L["l"] < bx[2] and L["b"] > bx[1] - 8 and L["t"] < bx[3] + 8:
                    f.append(f"TEPI: baris \"{' '.join(L['words'][:4])}…\" menabrak {nm}")
        if use_ill and s.get("illustration"):
            bg = textless(s, tmp, i); ill = raw_ill(s)
            top, wall = subject_top(ill)
            wallc = bg.crop((60, 160, 300, 200)).resize((1, 1)).getpixel((0, 0))
            for L in lines_all + [{"t": d[1], "b": d[3], "l": d[0], "r": d[2], "words": ["(ikon/kotak)"]} for d in m["dots"]]:
                std, far = busy(bg, (L["l"], L["t"], L["r"], L["b"]), wallc)
                if far > 0.30 or std > 22:
                    f.append(f"TABRAKAN: \"{' '.join(L['words'][:4])}…\" di atas area ramai (std {std:.0f}, {far:.0%} piksel beda)")
                elif std > BUSY_STD or far > BUSY_FRAC:
                    f.append(f"CATATAN: \"{' '.join(L['words'][:4])}…\" menyentuh tepi tokoh/benda (std {std:.0f}, {far:.0%}); lihat PNG, geser/penggal ulang kalau mengganggu")
            for sp in m.get("seps", []):
                std, far = busy(bg, sp, wallc)
                if far > 0.30:
                    f.append(f"TABRAKAN: garis pemisah daftar melewati tokoh/benda ({far:.0%} piksel beda); kecilkan body_width")
                elif far > 0.12:
                    f.append(f"CATATAN: garis pemisah daftar menyentuh tokoh/benda ({far:.0%}); pertimbangkan body_width lebih kecil")
            # tokoh tertutup veil: ramai di ilustrasi asli, tapi polos setelah veil -> tokoh jadi pudar/hantu
            rawwall = ill.crop((60, 160, 300, 200)).resize((1, 1)).getpixel((0, 0))
            ghost = 0
            for L in lines_all:
                _, far_raw = busy(ill, (L["l"], L["t"] - 20, L["r"], L["b"] + 20), rawwall)
                _, far_bg = busy(bg, (L["l"], L["t"] - 20, L["r"], L["b"] + 20), wallc)
                if far_raw > 0.30 and far_bg < BUSY_FRAC: ghost += 1
            if ghost:
                f.append(f"VEIL: {ghost} baris teks berada di atas tokoh/benda yang dipudarkan veil (tokoh tampak seperti hantu). Ilustrasi perlu tokoh di luar area teks")
            tb = max((L["b"] for L in lines_all), default=0) / H * 100
            # area kiri-bawah (di bawah teks) kosong melompong -> komposisi berat sebelah
            if s.get("layout", "kiri") == "kiri" and tb < 70:
                reg = ill.crop((0, int(tb / 100 * H) + 40, int(W * 0.40), int(H * 0.86))).resize((40, 40))
                farl = sum(1 for p in reg.getdata() if sum(abs(p[k] - rawwall[k]) for k in range(3)) > 60) / 1600
                if farl < 0.10:
                    f.append(f"CATATAN: area kiri di bawah teks hampir kosong ({farl:.0%} terisi). Perbesar ilustrasi (ill_zoom) atau tokoh lebih besar/ke kiri")
            if top - tb > 15:
                f.append(f"CATATAN: teks selesai di {tb:.0f}% tapi tokoh baru mulai di {top:.0f}% → celah {top-tb:.0f}%. Perbesar ilustrasi (ill_zoom) / tokoh lebih besar")
        allf[i] = list(dict.fromkeys(f))
    shutil.rmtree(tmp, ignore_errors=True)
    # caption
    cap = os.path.join(os.path.dirname(os.path.abspath(spec_path)), "caption.txt")
    capf = []
    if os.path.exists(cap):
        c = open(cap).read()
        if '"' in c: capf.append('GAYA caption: ada kutip lurus ("), pakai “…”')
        if "🤍" in c: capf.append("GAYA caption: 🤍 → 💗")
        if re.search(r"\b(geser|swipe)\b", c, re.I): capf.append("GAYA caption: kata geser/swipe")
    return allf, capf

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    allf, capf = check(sys.argv[1], "--no-ill" not in sys.argv)
    bad = 0
    notes = 0
    for i, f in allf.items():
        err = [x for x in f if not x.startswith("CATATAN")]; nt = [x for x in f if x.startswith("CATATAN")]
        bad += len(err); notes += len(nt)
        print(f"{'✗' if err else ('△' if nt else '✓')} slide {i}")
        for x in err: print("   ✗", x)
        for x in nt: print("   △", x)
    for x in capf: bad += 1; print("✗", x)
    print(f"\n{'LULUS' if not bad else str(bad) + ' kesalahan'}" + (f" · {notes} catatan (wajib dilihat di PNG oleh Tilik)" if notes else ""))
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
