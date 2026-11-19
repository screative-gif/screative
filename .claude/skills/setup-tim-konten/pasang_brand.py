#!/usr/bin/env python3
"""Pasang tim konten (Naka + Sera, Lira, Kala, Diksa, Rupa, Tilik) untuk brand baru.

Pakai:
  python3 pasang_brand.py --tujuan <folder-proyek> --jawaban jawaban.json   # salin template + isi placeholder
  python3 pasang_brand.py --tujuan <folder-proyek> --cek                    # cek placeholder sisa, aset, dan uji render

jawaban.json = {"BRAND": "...", "HANDLE": "...", ...}  (kunci = nama placeholder tanpa {{ }}).
Placeholder yang tidak diisi dibiarkan apa adanya dan dilaporkan oleh --cek.
Folder tujuan boleh sudah ada; file yang sudah ada TIDAK ditimpa kecuali --timpa.
"""
import argparse, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template")
TEXT_EXT = {".md", ".json", ".py", ".txt", ".example", ""}
PH = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def is_text(path):
    ext = os.path.splitext(path)[1]
    return ext in TEXT_EXT or os.path.basename(path) == ".env.example"


def copy_template(dest, answers, overwrite):
    n_new = n_skip = 0
    for root, _, files in os.walk(TEMPLATE):
        for fn in files:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, TEMPLATE)
            dst = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst) and not overwrite:
                n_skip += 1
                continue
            if is_text(src):
                s = open(src, encoding="utf-8").read()
                s = PH.sub(lambda m: str(answers.get(m.group(1), m.group(0))), s)
                open(dst, "w", encoding="utf-8").write(s)
            else:
                shutil.copy2(src, dst)
            n_new += 1
    print(f"✓ {n_new} file dipasang ke {dest}" + (f" ({n_skip} sudah ada, dilewati)" if n_skip else ""))


def check(dest):
    ok = True
    left = {}
    for root, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d not in ("data", ".git", "out")]
        for fn in files:
            p = os.path.join(root, fn)
            if not is_text(p):
                continue
            try:
                s = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            for m in PH.findall(s):
                left.setdefault(m, set()).add(os.path.relpath(p, dest))
    if left:
        ok = False
        print("✗ Placeholder yang belum diisi:")
        for k, fs in sorted(left.items()):
            print(f"   {{{{{k}}}}}  →  {', '.join(sorted(fs))}")
    else:
        print("✓ Tidak ada placeholder tersisa")

    bj = os.path.join(dest, "konten/brand/visual/brand.json")
    try:
        b = json.load(open(bj, encoding="utf-8"))
    except Exception as e:
        print(f"✗ brand.json tidak terbaca: {e}")
        return False
    need = [b.get("logo_header", ""), b.get("logo_footer", "")]
    fd = os.path.join(dest, "konten/brand/visual/font")
    need += [os.path.join("konten/brand/visual/font", b["fonts"]["heading"])]
    need += [os.path.join("konten/brand/visual/font", f) for f in b["fonts"]["body"].values()]
    for rel in need:
        if "{{" in rel or not os.path.exists(os.path.join(dest, rel)):
            ok = False
            print(f"✗ Aset belum ada: {rel}")
    for k, v in list(b["colors"].items()) + list(b["backgrounds"].items()):
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(v)):
            ok = False
            print(f"✗ Warna '{k}' bukan hex 6 digit: {v}")
    if not os.path.exists(os.path.join(dest, "riset/.env")):
        print("△ riset/.env belum ada (salin dari riset/.env.example lalu isi token Apify milik user sendiri)")
    if not ok:
        return False

    spec = json.load(open(os.path.join(HERE, "contoh_spec.json"), encoding="utf-8"))
    out = os.path.join(dest, "konten/visual/_uji-setup")
    spec["output_dir"] = out
    sp = os.path.join(out, "spec.json")
    os.makedirs(out, exist_ok=True)
    json.dump(spec, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, os.path.join(dest, "konten/brand/visual/render.py"), sp], capture_output=True, text=True)
    if r.returncode:
        print("✗ Uji render gagal:\n" + r.stderr[-1500:])
        return False
    for f in os.listdir(out):
        if f.endswith(".html"):
            os.remove(os.path.join(out, f))
    print(f"✓ Uji render berhasil: {out}/slide-01.png … (lihat hasilnya, lalu hapus folder _uji-setup)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tujuan", required=True)
    ap.add_argument("--jawaban")
    ap.add_argument("--timpa", action="store_true")
    ap.add_argument("--cek", action="store_true")
    a = ap.parse_args()
    dest = os.path.abspath(os.path.expanduser(a.tujuan))
    if a.jawaban:
        answers = json.load(open(a.jawaban, encoding="utf-8"))
        copy_template(dest, answers, a.timpa)
    if a.cek or not a.jawaban:
        sys.exit(0 if check(dest) else 1)


if __name__ == "__main__":
    main()
