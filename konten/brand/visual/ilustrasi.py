#!/usr/bin/env python3
"""Helper semi-otomatis bikin ilustrasi di ChatGPT (akun ChatGPT Go milik user).

Yang dikerjakan helper:
  - buka ChatGPT di Chrome + buka Finder dengan gambar referensi sudah terpilih (tinggal drag ke chat)
  - salin pesan pembuka & prompt ke clipboard satu per satu
  - pantau folder Downloads: begitu gambar baru selesai diunduh, otomatis dipindah & di-rename
    ke konten/visual/<folder>/ilustrasi/<HURUF>.<ext>, lalu prompt berikutnya langsung tersalin
Yang tetap manual (sengaja, supaya akun ChatGPT aman): Cmd+V, Enter, klik download.

Pakai (dari root proyek):
  python3 konten/brand/visual/ilustrasi.py C3                 # ilustrasi yang belum ada saja (default)
  python3 konten/brand/visual/ilustrasi.py C3 --daftar        # lihat semua prompt di prompt.md
  python3 konten/brand/visual/ilustrasi.py C3 --hanya A,F     # ulang huruf tertentu (pakai prompt versi terakhir)
  python3 konten/brand/visual/ilustrasi.py C3 --bagian "Putaran 2"   # jalankan satu bagian prompt.md
  python3 konten/brand/visual/ilustrasi.py C3 --tanpa-pembuka # lanjut di chat yang sama
  python3 konten/brand/visual/ilustrasi.py C3 --unduhan ~/Desktop    # kalau browser menyimpan di folder lain
Argumen pertama: kode (C3 → folder terbaru *_C3 di konten/visual/) atau path folder.

Saat menunggu gambar, ketik lalu Enter:
  u = salin ulang prompt ini     s = lewati prompt ini     q = berhenti
File lama yang tertimpa disimpan di ilustrasi/_lama/.

Format prompt.md yang dibaca (ditulis Rupa):
  - blok kode di bawah judul yang mengandung "Pesan pembuka" = pesan pembuka
  - blok kode di bawah judul "## A · ..." atau "### A.png · ..." = prompt untuk A.png
  - putaran revisi = bagian "## ..." baru di bawahnya
"""
import argparse, glob, json, os, re, select, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
VISUAL = os.path.join(ROOT, "konten", "visual")
REFERENSI = os.path.join(HERE, "referensi")
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
PARTIAL = (".crdownload", ".download", ".part", ".tmp")
CHATGPT_URL = "https://chatgpt.com/"

LETTER_RE = re.compile(r"^#{2,4}\s+([A-Z])(?:\.(?:png|jpe?g|webp))?\s*(?:·|-|–|:|\s*$)")


# ---------- util macOS ----------
def sh(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def copy(text):
    env = dict(os.environ, LANG="en_US.UTF-8", LC_CTYPE="UTF-8")
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), env=env)


def notify(title, msg, sound="Glass"):
    t = title.replace('"', "'")
    m = msg.replace('"', "'")
    sh("osascript", "-e", f'display notification "{m}" with title "{t}" sound name "{sound}"')


def open_chatgpt():
    r = sh("open", "-a", "Google Chrome", CHATGPT_URL)
    if r.returncode != 0:
        sh("open", CHATGPT_URL)


def reveal(files):
    files = [f for f in files if os.path.exists(f)]
    if not files:
        return
    items = ", ".join(f'(POSIX file "{f}" as alias)' for f in files)
    sh("osascript", "-e", f'tell application "Finder" to reveal {{{items}}}',
       "-e", f'tell application "Finder" to select {{{items}}}',
       "-e", 'tell application "Finder" to activate')


def image_size(path):
    r = sh("sips", "-g", "pixelWidth", "-g", "pixelHeight", path)
    w = re.search(r"pixelWidth:\s*(\d+)", r.stdout)
    h = re.search(r"pixelHeight:\s*(\d+)", r.stdout)
    return (int(w.group(1)), int(h.group(1))) if w and h else (0, 0)


# ---------- baca prompt.md ----------
def find_folder(arg):
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    p = os.path.join(ROOT, arg)
    if os.path.isdir(p):
        return p
    hits = sorted(d for d in glob.glob(os.path.join(VISUAL, f"*_{arg.upper()}")) if os.path.isdir(d))
    if not hits:
        sys.exit(f"Folder untuk '{arg}' tidak ditemukan di konten/visual/. Minta Rupa 'siapkan visual {arg}' dulu.")
    return hits[-1]


def parse_prompt(md):
    """-> list blok: {section, heading, letter, kind, text}"""
    blocks, section, heading = [], "", ""
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## ") and not ln.startswith("### "):
            section = heading = ln[3:].strip()
        elif re.match(r"^#{3,4}\s", ln):
            heading = ln.lstrip("#").strip()
        elif ln.strip().startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            hline = "## " + heading
            m = LETTER_RE.match(hline)
            if "pembuka" in heading.lower():
                kind, letter = "pembuka", None
            elif m:
                kind, letter = "gambar", m.group(1)
            else:
                kind, letter = "teks", None
            blocks.append({"section": section, "heading": heading, "letter": letter,
                           "kind": kind, "text": "\n".join(body).strip()})
        i += 1
    return blocks


def reference_files(md):
    names = re.findall(r"`([^`/]+\.(?:png|jpe?g|webp))`", md)
    out = []
    for n in names:
        p = os.path.join(REFERENSI, n)
        if os.path.exists(p) and p not in out:
            out.append(p)
    return out


def existing(ilu, letter):
    for ext in IMG_EXT:
        p = os.path.join(ilu, letter + ext)
        if os.path.exists(p):
            return p
    return None


# ---------- pantau unduhan ----------
def snapshot(dirs):
    snap = {}
    for d in dirs:
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if os.path.isfile(p):
                snap[p] = os.path.getmtime(p)
    return snap


def new_images(dirs, before):
    out = []
    for d in dirs:
        for f in os.listdir(d):
            p = os.path.join(d, f)
            if f.startswith(".") or not f.lower().endswith(IMG_EXT) or f.lower().endswith(PARTIAL):
                continue
            if os.path.isfile(p) and (p not in before or os.path.getmtime(p) > before[p] + 0.5):
                out.append(p)
    return out


def stable(path):
    try:
        s1 = os.path.getsize(path)
        time.sleep(1.0)
        return s1 > 0 and s1 == os.path.getsize(path)
    except OSError:
        return False


def read_key():
    r, _, _ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.readline().strip().lower() if r else None


def save_as(src, ilu, letter):
    ext = os.path.splitext(src)[1].lower().replace(".jpeg", ".jpg")
    old = existing(ilu, letter)
    if old and os.path.abspath(old) != os.path.abspath(src):
        lama = os.path.join(ilu, "_lama")
        os.makedirs(lama, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        shutil.move(old, os.path.join(lama, f"{letter}_{stamp}{os.path.splitext(old)[1]}"))
    dst = os.path.join(ilu, letter + ext)
    if os.path.abspath(src) != os.path.abspath(dst):
        shutil.move(src, dst)
    return dst


def run_step(n, total, b, ilu, watch_dirs):
    label = f"[{n}/{total}]"
    copy(b["text"])
    if b["kind"] != "gambar":
        nama = "Pesan pembuka" if b["kind"] == "pembuka" else b["heading"]
        print(f"\n{label} {nama} sudah tersalin.")
        print("   → Lampirkan gambar referensi (drag dari Finder), Cmd+V, Enter di ChatGPT.")
        notify("Ilustrasi", f"{nama} tersalin. Cmd+V lalu Enter")
        input("   Tekan Enter di sini kalau ChatGPT sudah balas (s = lewati)... ")
        return True

    letter = b["letter"]
    print(f"\n{label} Prompt {letter}  ({b['heading']}) sudah tersalin.")
    print(f"   → Cmd+V, Enter di ChatGPT. Setelah gambar jadi, klik download.")
    print(f"   Menunggu {letter} di Downloads...  (u = salin ulang, s = lewati, q = berhenti)")
    notify("Ilustrasi", f"Prompt {letter} tersalin. Cmd+V lalu Enter")
    before = snapshot(watch_dirs)
    while True:
        k = read_key()
        if k == "u":
            copy(b["text"])
            print(f"   Prompt {letter} disalin ulang.")
        elif k == "s":
            print(f"   {letter} dilewati.")
            return True
        elif k == "q":
            return False
        for p in new_images(watch_dirs, before):
            if os.path.dirname(p) == ilu and not os.path.basename(p).upper().startswith(letter + "."):
                continue  # file huruf lain yang ditaruh manual di ilustrasi/
            if not stable(p):
                continue
            dst = save_as(p, ilu, letter)
            w, h = image_size(dst)
            info = f"{w}×{h}" if w else "ukuran tidak terbaca"
            print(f"   ✓ Tersimpan: {os.path.relpath(dst, ROOT)}  ({info})")
            if w and h <= w:
                print("   ⚠️  Gambar ini tidak vertikal. Di ChatGPT balas: \"Redo it in vertical 4:5 portrait. No text.\"")
                print(f"      lalu jalankan lagi dengan --hanya {letter}.")
            notify("Ilustrasi", f"{letter} tersimpan ({info})", sound="Hero")
            return True
        time.sleep(1.0)




# ---------- pilih langkah ----------
def select_steps(a, blocks, ilu, rel):
    """-> (steps, revisi). steps sudah termasuk pesan pembuka kalau chat baru."""
    pembuka = [b for b in blocks if b["kind"] == "pembuka"][:1]
    gambar = [b for b in blocks if b["kind"] == "gambar"]
    if a.bagian:
        q = a.bagian.lower()
        steps = [b for b in blocks if q in b["section"].lower() and b["kind"] != "pembuka"]
        if not steps:
            sys.exit(f"Tidak ada bagian yang judulnya mengandung '{a.bagian}'. Cek dengan --daftar.")
    elif a.hanya:
        steps = []
        for L in [x.strip().upper() for x in a.hanya.split(",") if x.strip()]:
            cand = [b for b in gambar if b["letter"] == L]
            if not cand:
                sys.exit(f"Tidak ada prompt untuk {L}.png di prompt.md.")
            steps.append(cand[-1])
    else:
        seen, steps = set(), []
        for b in gambar:
            if b["letter"] in seen:
                continue
            seen.add(b["letter"])
            if not existing(ilu, b["letter"]):
                steps.append(b)
        if not steps:
            print(f"Semua ilustrasi di {rel}/ilustrasi/ sudah lengkap. Pakai --hanya A,B untuk mengulang.")
            sys.exit(0)
    revisi = bool(a.hanya or a.bagian)
    if not a.tanpa_pembuka and (not revisi or a.chat_baru):
        steps = pembuka + steps
    return steps, revisi


# ---------- mode Mausbot ----------
MAUSBOT = os.path.expanduser(os.environ.get("MAUSBOT_DIR", "~/Mausbot"))
TUGAS_SRC = os.path.join(HERE, "mausbot_TUGAS.md")
SKILL_SRC = os.path.join(HERE, "mausbot_SKILL.md")


def mausbot_dirs():
    d = {k: os.path.join(MAUSBOT, k) for k in ("antrian", "selesai", "arsip")}
    for p in d.values():
        os.makedirs(p, exist_ok=True)
    for src, name in ((TUGAS_SRC, "TUGAS.md"), (SKILL_SRC, "SKILL.md")):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(MAUSBOT, name))
    return d


def make_package(folder, ilu, md, steps, revisi):
    d = mausbot_dirs()
    kode = os.path.basename(folder).split("_")[-1]
    pkg = os.path.join(d["antrian"], kode)
    if os.path.isdir(pkg):
        hasil = os.path.join(pkg, "hasil")
        if os.path.isdir(hasil) and any(not f.startswith(".") for f in os.listdir(hasil)):
            sys.exit(f"Paket {kode} masih dikerjakan Mausbot ({pkg}/hasil/ sudah berisi). "
                     "Tunggu selesai, atau hapus foldernya dulu kalau memang mau diganti.")
        shutil.rmtree(pkg)
    os.makedirs(os.path.join(pkg, "hasil"))

    chat_src = os.path.join(ilu, "chat.txt")
    baru = bool(steps) and steps[0]["kind"] == "pembuka"
    if revisi and not baru and not os.path.exists(chat_src):
        # tidak tahu chat lamanya -> mulai chat baru supaya gaya & tokoh tetap konsisten
        pembuka = [b for b in parse_prompt(md) if b["kind"] == "pembuka"][:1]
        steps = pembuka + steps
        baru = bool(pembuka)

    files, n = [], 0
    for b in steps:
        if b["kind"] == "pembuka":
            name = "00_pembuka.txt"
        else:
            n += 1
            name = f"{n:02d}_{b['letter'] if b['letter'] else 'pesan'}.txt"
        with open(os.path.join(pkg, name), "w", encoding="utf-8") as f:
            f.write(b["text"] + "\n")
        files.append(name)

    if baru:
        rd = os.path.join(pkg, "referensi")
        os.makedirs(rd)
        for r in reference_files(md):
            shutil.copy(r, rd)
    elif os.path.exists(chat_src):
        shutil.copy(chat_src, os.path.join(pkg, "chat.txt"))

    huruf = [b["letter"] for b in steps if b["letter"]]
    info = {"kode": kode, "folder": os.path.relpath(folder, ROOT), "huruf": huruf,
            "chat_baru": baru, "dibuat": time.strftime("%Y-%m-%d %H:%M")}
    with open(os.path.join(pkg, "info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"📦 Paket Mausbot siap: {pkg}")
    print(f"   Isi    : {', '.join(files)}")
    print(f"   Target : {', '.join(h + '.png' for h in huruf)}")
    print(f"   Chat   : {'BARU (lampirkan referensi/)' if baru else 'lanjut chat lama (chat.txt)'}")
    print("\nSuruh Mausbot: \"Kerjakan antrian ilustrasi\" (skill: ~/Mausbot/SKILL.md)")
    print("Lalu biarkan pemantau jalan:  python3 konten/brand/visual/ilustrasi.py --pantau")


def find_result(hasil, letter):
    for f in sorted(os.listdir(hasil)):
        base, ext = os.path.splitext(f)
        if base.upper() == letter and ext.lower() in IMG_EXT:
            return os.path.join(hasil, f)
    return None


OTOMATIS = False  # diset oleh --otomatis: lanjut render + kirim Discord tanpa user
OTOMASI = os.path.join(ROOT, "otomasi")


def discord(msg):
    """Kirim ke Discord tim (kalau --otomatis). Tidak pernah bikin pemantau mati."""
    if not OTOMATIS:
        return
    try:
        sys.path.insert(0, OTOMASI)
        import notif as dc
        dc.send(msg)
    except BaseException as e:  # noqa: BLE001 (SystemExit dari dc juga ditangkap)
        print(f"   (gagal kirim Discord: {e})", flush=True)


def lanjut_otomatis(folder):
    if not OTOMATIS:
        return
    logf = open(os.path.join(OTOMASI, "log", "lanjut.out"), "a")
    subprocess.Popen([sys.executable, os.path.join(OTOMASI, "lanjut.py"), folder], cwd=ROOT,
                     stdout=logf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)


def collect(pkg, arsip):
    """Ambil hasil satu paket selesai -> folder ilustrasi proyek. Return ringkasan teks."""
    kode = os.path.basename(pkg)
    try:
        info = json.load(open(os.path.join(pkg, "info.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return f"⚠️  {kode}: info.json tidak ada/rusak, paket dilewati."
    folder = os.path.join(ROOT, info["folder"])
    ilu = os.path.join(folder, "ilustrasi")
    os.makedirs(ilu, exist_ok=True)
    hasil = os.path.join(pkg, "hasil")
    os.makedirs(hasil, exist_ok=True)
    masuk, kurang, miring = [], [], []
    for L in info.get("huruf", []):
        src = find_result(hasil, L)
        if not src:
            kurang.append(L)
            continue
        dst = save_as(src, ilu, L)
        w, h = image_size(dst)
        if w and h <= w:
            miring.append(L)
        masuk.append(L)
    for extra in ("chat.txt",):
        for src in (os.path.join(hasil, extra), os.path.join(pkg, extra)):
            if os.path.exists(src):
                shutil.copy(src, os.path.join(ilu, extra))
                break
    catatan = os.path.join(hasil, "catatan.txt")
    cat_txt = open(catatan, encoding="utf-8").read().strip() if os.path.exists(catatan) else ""
    if cat_txt:
        shutil.copy(catatan, os.path.join(ilu, "catatan-mausbot.txt"))
    dest = os.path.join(arsip, f"{kode}_{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.move(pkg, dest)

    lines = [f"✓ {kode}: masuk {', '.join(masuk) or '-'} → {info['folder']}/ilustrasi/"]
    if kurang:
        lines.append(f"   ⚠️  belum ada: {', '.join(k + '.png' for k in kurang)} (buat paket lagi: {kode} --paket --hanya {','.join(kurang)})")
    if miring:
        lines.append(f"   ⚠️  tidak vertikal: {', '.join(miring)}")
    if cat_txt:
        lines.append(f"   📝 catatan Mausbot: {cat_txt[:300]}")
    lengkap = not kurang
    if OTOMATIS:
        lines.append("   → Lengkap. Naka otomatis lanjut render (log: otomasi/log/)." if lengkap else "   → Belum lengkap.")
    else:
        lines.append(f'   → Lengkap. Bilang "Naka, render {kode}".' if lengkap else "   → Belum lengkap.")
    if lengkap:
        lanjut_otomatis(folder)
    else:
        discord(f"⚠️ **{kode}**: Mausbot menutup paket tapi gambar **{', '.join(kurang)}** belum ada. "
                f"Naka bisa bikin paket lagi: `ilustrasi.py {kode} --paket --hanya {','.join(kurang)}`.")
    notify("Ilustrasi",
           f"{kode}: {len(masuk)} ilustrasi masuk" + (". Siap render!" if lengkap else f", kurang {','.join(kurang)}"),
           sound="Hero")
    return "\n".join(lines)


def collect_all(reported):
    d = mausbot_dirs()
    out = []
    # paket yang ditandai SELESAI.txt tapi belum dipindah ke selesai/
    for k in sorted(os.listdir(d["antrian"])):
        pkg = os.path.join(d["antrian"], k)
        if os.path.isdir(pkg) and os.path.exists(os.path.join(pkg, "SELESAI.txt")):
            shutil.move(pkg, os.path.join(d["selesai"], k))
    for k in sorted(os.listdir(d["selesai"])):
        pkg = os.path.join(d["selesai"], k)
        if os.path.isdir(pkg):
            out.append(collect(pkg, d["arsip"]))
    for k in sorted(os.listdir(d["antrian"])):
        stop = os.path.join(d["antrian"], k, "BERHENTI.txt")
        if os.path.exists(stop):
            key = (k, os.path.getmtime(stop))
            if key not in reported:
                reported.add(key)
                alasan = open(stop, encoding="utf-8").read().strip()[:200]
                notify("Mausbot berhenti", f"{k}: {alasan}", sound="Basso")
                discord(f"⛔ **Mausbot berhenti** di paket **{k}**: {alasan}\n"
                        "Bereskan masalahnya, hapus `BERHENTI.txt` di paketnya, lalu suruh Mausbot lanjut.")
                out.append(f"⛔ {k}: Mausbot berhenti: {alasan}\n   Bereskan masalahnya, hapus BERHENTI.txt, lalu suruh Mausbot lanjut.")
    return out


def pantau(sekali):
    print(f"Memantau {MAUSBOT}/selesai/ ... (Ctrl+C untuk berhenti)" if not sekali else f"Cek {MAUSBOT} ...")
    reported = set()
    while True:
        for line in collect_all(reported):
            print(time.strftime("[%H:%M] ") + line, flush=True)
        if sekali:
            return
        time.sleep(10)


def main():
    ap = argparse.ArgumentParser(description="Helper ilustrasi ChatGPT (manual atau lewat Mausbot)")
    ap.add_argument("kode", nargs="?", help="kode konten (mis. C3) atau path folder visual")
    ap.add_argument("--daftar", action="store_true", help="tampilkan semua prompt lalu keluar")
    ap.add_argument("--hanya", help="huruf yang mau dibuat/diulang, mis. A,F (pakai prompt versi terakhir)")
    ap.add_argument("--bagian", help="jalankan semua prompt di bagian prompt.md yang judulnya mengandung teks ini")
    ap.add_argument("--tanpa-pembuka", action="store_true", help="jangan kirim pesan pembuka (lanjut di chat yang sama)")
    ap.add_argument("--chat-baru", action="store_true", help="untuk --hanya/--bagian: mulai chat baru (kirim pesan pembuka)")
    ap.add_argument("--unduhan", default=os.path.expanduser("~/Downloads"), help="folder unduhan browser")
    ap.add_argument("--tanpa-buka", action="store_true", help="jangan buka ChatGPT & Finder otomatis")
    ap.add_argument("--paket", action="store_true", help="buat paket tugas untuk Mausbot di ~/Mausbot/antrian/<KODE>/")
    ap.add_argument("--ambil", action="store_true", help="ambil sekali hasil Mausbot dari ~/Mausbot/selesai/")
    ap.add_argument("--pantau", action="store_true", help="pantau terus ~/Mausbot/selesai/ dan ambil hasilnya otomatis")
    ap.add_argument("--otomatis", action="store_true", help="dengan --pantau/--ambil: lanjut render otomatis (otomasi/lanjut.py) + lapor ke Discord")
    a = ap.parse_args()

    if a.ambil or a.pantau:
        global OTOMATIS
        OTOMATIS = a.otomatis
        return pantau(sekali=a.ambil)
    if not a.kode:
        ap.error("kode konten wajib diisi (mis. C3), kecuali untuk --ambil / --pantau")

    folder = find_folder(a.kode)
    pmd = os.path.join(folder, "prompt.md")
    if not os.path.exists(pmd):
        sys.exit(f"Belum ada prompt.md di {os.path.relpath(folder, ROOT)}. Minta Rupa 'siapkan visual' dulu.")
    md = open(pmd, encoding="utf-8").read()
    blocks = parse_prompt(md)
    ilu = os.path.join(folder, "ilustrasi")
    os.makedirs(ilu, exist_ok=True)
    rel = os.path.relpath(folder, ROOT)

    if a.daftar:
        print(f"Prompt di {rel}/prompt.md:")
        for i, b in enumerate(blocks, 1):
            tag = b["letter"] + ".png" if b["letter"] else b["kind"]
            ada = " (sudah ada)" if b["letter"] and existing(ilu, b["letter"]) else ""
            judul = b["heading"] if b["heading"] == b["section"] else f"{b['section']} › {b['heading']}"
            print(f"  {i:2}. [{tag}] {judul}{ada}")
        return

    steps, revisi = select_steps(a, blocks, ilu, rel)
    if a.paket:
        return make_package(folder, ilu, md, steps, revisi)

    # ---- mode manual (kamu sendiri yang Cmd+V di ChatGPT) ----
    refs = reference_files(md)
    baru = bool(steps) and steps[0]["kind"] == "pembuka"
    huruf = [b["letter"] for b in steps if b["letter"]]
    print(f"Konten : {rel}")
    print(f"Target : {', '.join(h + '.png' for h in huruf) or '-'}  → {os.path.relpath(ilu, ROOT)}/")
    print(f"Pantau : {a.unduhan}")
    if refs and baru:
        print("Referensi untuk dilampirkan di chat baru:")
        for r in refs:
            print(f"   - {os.path.basename(r)}")
    if not os.path.isdir(a.unduhan):
        sys.exit(f"Folder unduhan {a.unduhan} tidak ada. Pakai --unduhan <folder>.")
    watch = [a.unduhan, ilu]

    if not a.tanpa_buka:
        open_chatgpt()
        if baru:
            reveal(refs)
    if baru:
        print("\nBuka chat BARU di ChatGPT dulu.")

    for n, b in enumerate(steps, 1):
        if not run_step(n, len(steps), b, ilu, watch):
            print("\nBerhenti. Jalankan lagi kapan saja; yang sudah tersimpan tidak diulang.")
            break

    gambar = [b for b in blocks if b["kind"] == "gambar"]
    kurang = sorted({b["letter"] for b in gambar if not existing(ilu, b["letter"])})
    kode = os.path.basename(folder).split("_")[-1]
    print()
    if not kurang:
        notify("Ilustrasi", f"Semua ilustrasi {kode} lengkap!", sound="Hero")
        print(f"🎉 Semua ilustrasi {kode} lengkap. Langkah berikutnya: bilang \"Naka, render {kode}\".")
    else:
        print(f"Masih kurang: {', '.join(k + '.png' for k in kurang)}. Jalankan lagi perintah yang sama untuk melanjutkan.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDihentikan.")
