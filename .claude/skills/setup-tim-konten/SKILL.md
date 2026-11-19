---
name: setup-tim-konten
description: Pasang tim konten sosmed lengkap (Naka koordinator + Sera riset data, Lira analis tren, Kala perencana feeding, Diksa penulis, Rupa desainer visual, Tilik QA visual) untuk brand baru di folder proyek Claude Code. Gunakan saat user minta "setup tim konten", "pasang Naka untuk brand X", "clone tim konten", atau mau mulai mengelola Instagram/Threads brand baru dengan alur riset → feeding → draft → visual carousel/feed.
---

# Setup Tim Konten untuk Brand Baru

Skill ini memasang tim konten yang sudah teruji: riset tren (Apify) → laporan → feeding mingguan → draft → visual carousel/feed 1080×1350 dengan template brand + QA otomatis. Kamu (Claude) yang memandu user dari folder kosong sampai uji render berhasil.

File skill:
- `template/` : seluruh isi proyek (CLAUDE.md Naka, `.claude/agents/`, `riset/`, `konten/brand/` + `visual/` dengan render.py, check.py, ilustrasi.py)
- `pasang_brand.py` : menyalin template ke folder proyek dan mengisi placeholder `{{...}}`, lalu `--cek` untuk validasi + uji render
- `contoh_spec.json` : spec uji render

## Prinsip
- **Jangan pernah meminta, menampilkan, atau menyimpan token/kata sandi user di chat.** Token Apify diisi user sendiri ke `riset/.env`.
- Jangan menyalin isi brand lain. Semua isi brand baru berasal dari jawaban user, situs/akun brand itu, dan aset yang user berikan.
- Tanyakan secukupnya dan berkelompok (pakai AskUserQuestion bila tersedia, maks 4 pertanyaan sekali). Kalau user memberi situs web, baca dulu situsnya untuk mengisi draf jawaban, lalu minta user mengonfirmasi.
- Keputusan kreatif (warna, tagline, suara brand) tetap milik user.

## Langkah

### 1. Tentukan folder proyek
- Pakai folder kerja saat ini kalau kosong atau baru. Kalau sudah berisi proyek lain, tanya user dulu.
- Satu brand = satu folder. Jangan pasang dua brand di folder yang sama.

### 2. Kumpulkan info brand (wawancara singkat)
Kumpulkan, lalu tulis ke file scratch `jawaban.json` (kunci = nama placeholder):

| Kelompok | Placeholder |
|---|---|
| Identitas | `BRAND`, `HANDLE` (tanpa @), `WEBSITE`, `SLUG` (huruf kecil tanpa spasi), `DESKRIPSI_SINGKAT` (1 kalimat), `TAGLINE` |
| Header visual | `TAGLINE_BARIS_1`, `TAGLINE_BARIS_2` (2 baris kecil di kanan atas setiap slide; boleh dikosongkan jadi string kosong) |
| Profil | `FITUR_INTI`, `HARGA`, `CERITA_BRAND`, `AUDIENS`, `POSISI_PESAING`, `KONDISI_AKUN` |
| Konten | `NICHE` (1 kalimat), `PILAR_KONTEN` (baris tabel markdown `\| **1. Nama** \| 35% \| isi \| format \|`, satu per pilar), `ATURAN_JUALAN`, `SUARA_BRAND`, `BATASAN_WAJIB` (bullet; **wajib** menyebut topik sensitif brand ini, mis. kesehatan/keuangan/hukum, beserta sumber tepercaya dan arahan ke ahli) |
| Riset | `KEYWORD_1..3`, `HASHTAG_1..2` (tanpa #) |
| Warna (hex) | `WARNA_PRIMER`, `WARNA_PRIMER_LEMBUT`, `WARNA_SEKUNDER`, `WARNA_AKSEN`, `WARNA_AKSEN_GELAP`, `WARNA_STABILO`, `WARNA_TEKS`, `LATAR_1..3` (pucat) |
| Font & logo | `FONT_JUDUL`, `FONT_TEKS_400/500/600/700` (nama file .ttf/.otf), `NAMA_FONT_JUDUL`, `NAMA_FONT_TEKS`, `LOGO_HEADER`, `LOGO_FOOTER` (nama file PNG transparan) |
| Ilustrasi | `PROMPT_GAYA_ILUSTRASI` (bahasa Inggris), `TOKOH_1`, `CIRI_TOKOH_1`, `TOKOH_2`, `CIRI_TOKOH_2`, `LARANGAN_TAMBAHAN` (bullet, boleh kosong) |

Tips:
- Kalau user punya brand kit (PDF/Drive/Figma), ambil warna & font dari sana.
- Kalau font tidak punya berat 500/600, pakai file yang sama untuk beberapa berat.
- `WARNA_AKSEN_GELAP` harus cukup gelap agar terbaca sebagai teks di latar pucat. `WARNA_PRIMER_LEMBUT` dipakai untuk lingkaran ikon.
- Kalau user belum punya gaya ilustrasi, tawarkan 2–3 opsi gaya dan biarkan user memilih. Wajah tokoh tetap *faceless* (aturan tim).
- Tokoh lebih dari dua? Tambahkan baris tabel di `visual.md` setelah pemasangan.

### 3. Pasang template
```bash
python3 <folder-skill>/pasang_brand.py --tujuan <folder-proyek> --jawaban <scratch>/jawaban.json
```
Lalu minta user menaruh aset ke folder proyek (atau salin kalau user memberi path-nya):
- logo → `konten/brand/visual/logo/`
- font → `konten/brand/visual/font/` (pastikan lisensinya boleh dipakai)
- 3–9 contoh post brand (PNG) → `konten/brand/visual/referensi/` (dipakai sebagai referensi gaya saat generate ilustrasi)

### 4. Validasi & uji render
```bash
pip3 install pillow   # kalau belum ada
python3 <folder-skill>/pasang_brand.py --tujuan <folder-proyek> --cek
```
- Perbaiki semua ✗ (placeholder sisa, aset hilang, warna bukan hex).
- Buka 3 PNG di `konten/visual/_uji-setup/` dan tunjukkan ke user. Tanyakan apakah warna, font, logo, tagline, dan footer sudah benar. Sesuaikan `brand.json` (atau CSS di `render.py` kalau gaya header/footer brand sangat berbeda), render ulang, sampai user setuju.
- Setelah setuju, hapus `konten/visual/_uji-setup/`.

### 5. Riset (Apify)
- Minta user membuat akun gratis di console.apify.com, lalu **user sendiri** menyalin `riset/.env.example` jadi `riset/.env` dan menempel tokennya. Jangan meminta token di chat.
- Uji gratis: `cd riset && python3 collect.py --dry-run`.
- Sesuaikan `riset/config.json` (keyword, hashtag, akun referensi di `ig_akun.accounts`).

### 6. Selesai
- Beri tahu user: **tutup lalu buka lagi sesi Claude Code di folder proyek** supaya agent di `.claude/agents/` dan `CLAUDE.md` (Naka) termuat.
- Contoh perintah pertama: "Naka, riset tren", "Naka, feeding minggu ini", "Naka, siapkan visual C1".
- Ingatkan: aturan kerapian visual di `konten/brand/visual.md` adalah hasil revisi panjang; jangan dihapus. Keputusan baru dari user ditambahkan ke sana atau ke `brand.md`.

## Yang tidak termasuk (modul lanjutan, pasang terpisah kalau diminta)
- Auto-posting Instagram, bot review Discord, pemantau latar belakang (launchd), dan bot generate ilustrasi otomatis. Modul ini butuh token akun masing-masing dan nama layanan launchd yang unik per brand, jadi tidak dipasang otomatis.
