# Panduan Visual {{BRAND}} (Instagram @{{HANDLE}})

*Rupa dan Tilik wajib membaca file ini sebelum membuat atau memeriksa visual. Identitas teknis (warna, font, logo, tagline, footer) ada di `konten/brand/visual/brand.json` dan dipakai otomatis oleh `render.py`.*

## Aset
| Aset | Lokasi |
|---|---|
| Logo untuk header (kiri atas) | `konten/brand/visual/logo/{{LOGO_HEADER}}` |
| Logo putih/terang untuk label footer | `konten/brand/visual/logo/{{LOGO_FOOTER}}` |
| Font judul | {{NAMA_FONT_JUDUL}} (`konten/brand/visual/font/{{FONT_JUDUL}}`) |
| Font teks | {{NAMA_FONT_TEKS}} (`konten/brand/visual/font/`) |
| Contoh post brand | `konten/brand/visual/referensi/` |
| Identitas brand untuk template | `konten/brand/visual/brand.json` |
| Mesin render | `konten/brand/visual/render.py` (spec JSON jadi PNG 1080×1350) |
| Cek QA otomatis | `konten/brand/visual/check.py` (orphan, stabilo, tepi, tabrakan teks dengan tokoh, veil, area kosong, gaya). Dipakai Rupa dan Tilik |
| Helper ilustrasi ChatGPT | `konten/brand/visual/ilustrasi.py` (salin prompt ke clipboard, pindahkan hasil unduhan) |

## Warna
| Peran (di brand.json) | Hex | Dipakai untuk |
|---|---|---|
| `primary` | `{{WARNA_PRIMER}}` | judul, label footer, kata yang ditekankan (`**teks**`), nomor judul |
| `secondary` | `{{WARNA_SEKUNDER}}` | garis putus-putus, bingkai kotak MITOS |
| `accent` / `accent_dark` | `{{WARNA_AKSEN}}` / `{{WARNA_AKSEN_GELAP}}` | kata kunci di judul (`__teks__`), ikon, kotak FAKTA, garis pemisah |
| `highlight` | `{{WARNA_STABILO}}` | stabilo kata kunci (`==teks==`) |
| `text` | `{{WARNA_TEKS}}` | teks isi |

Latar (`backgrounds` di brand.json) selalu **lembut/pucat**: {{LATAR_1}}, {{LATAR_2}}, {{LATAR_3}}. Jangan memakai warna jenuh untuk area besar.

## Layout wajib (setiap post)
1. **Kiri atas:** logo brand
2. **Kanan atas:** tagline brand (dari brand.json). Jangan diganti tanpa izin user.
3. **Kanan bawah:** label warna primer yang menempel ke tepi kanan, berisi 🌐 {{WEBSITE}} | Instagram @{{HANDLE}}
   - Varian untuk quote atau kutipan: label berisi logo putih | @{{HANDLE}}, tanpa header (`footer: "logo-ig"`, `header: false`)

Tipe slide yang tersedia di `render.py`:
| layout | Isi |
|---|---|
| `kiri` | judul besar di kiri atas, teks/daftar di kiri, ilustrasi mengisi kanan & bawah |
| `tengah` | judul di tengah atas, kartu MITOS/FAKTA, ilustrasi di bawah |
| `threads` | kartu screenshot Threads di atas ilustrasi |

Gaya teks:
- Judul maksimal 3 baris dan 2 warna (primer + aksen atau abu gelap).
- Satu kata atau frasa kunci per slide distabilo.
- Teks isi maksimal sekitar 40 kata per slide.

## Aturan kerapian (wajib)
Aturan ini lahir dari banyak putaran revisi di proyek sebelumnya. Ikuti semuanya; Tilik memeriksanya di setiap slide.
- **Layout ikut ilustrasi.**
  - Judul rata tengah (`tengah`) hanya kalau tokoh di ilustrasi ada di tengah-bawah.
  - Kalau tokoh di kanan, pakai `kiri`.
  - Prompt ilustrasi harus ditulis sesuai layout slide yang direncanakan.
- **Hemat baris judul.**
  - Judul pendek (≤ 3 kata) cukup 1 baris; kecilkan ukurannya kalau perlu.
  - Judul sedang cukup 2 baris.
  - Jangan pecah judul jadi 1 kata per baris.
- **Tidak boleh ada 1 kata sendirian di satu baris**, baik di judul, teks isi, kotak MITOS/FAKTA, maupun daftar. Kecilkan teks atau atur ulang penggalan supaya baris terakhir punya minimal 2 kata.
- **Ukuran default:** judul 100 px, teks isi 27 px. Jangan dibesarkan kecuali judulnya sangat pendek.
- **Stabilo:**
  - Kalau jadi label sendiri (satu paragraf penuh), paddingnya lebar. Kalau di tengah kalimat, paddingnya tipis. Template mengatur ini otomatis.
  - Jangan biarkan stabilo terpotong ke 2 baris.
- **Penggalan baris mengikuti makna**, bukan otomatis. Pakai `\n` di spec. Contoh: "Wajar Banget / kalau Cemas", "Padahal kamu sudah berusaha / ==sebaik mungkin== / buat si kecil."
- **Jarak judul ke teks isi harus lega.** Tambah `body_gap` sekitar 50 px kalau teks isinya langsung berupa kalimat. Kalimat kunci di bawah judul boleh sedikit lebih besar (`body_size` sekitar 31).
- **CTA slide terakhir:**
  - Langsung ke satu ajakan, misalnya "**Bagikan** ke teman yang … 💗", dengan `cta_icon: "share"`.
  - Jangan tumpuk 2 ajakan seperti "Simpan carousel ini. Bagikan …".
  - Teks CTA selalu rata kiri, juga di layout `tengah` (otomatis).
- **Nomor di judul ("1. …") ikut warna primer judul.** Warna aksen hanya untuk kata kunci.
- **Di layout `tengah`, kalimat pendek cukup 1 baris.** Jangan dipenggal kalau masih muat di lebar 900 px.
- **Tokoh terlalu kecil atau ruang kiri masih kosong?** Pakai `ill_zoom` (misalnya 1.25, jangkar kanan-bawah), lalu cek lagi supaya kepala tidak naik ke area teks. Tidak perlu generate ulang.
- **Isi ruang kosong.** Kalau area teks di kiri masih banyak yang kosong, tambah 1–2 kalimat pendek yang mendukung pesan, tetap di bawah sekitar 40 kata.
- **Kotak FAKTA warna aksen, kotak MITOS warna primer** (otomatis).
- **Ikon daftar kecil** (60 px) dan **bervariasi sesuai makna** (`scale`, `droplet`, `battery`, `trending-down`, `moon`, `sun`, `heart`, `book`, `shield`, …). Jangan pakai ikon yang sama untuk semua poin.
- **Tanpa CTA geser.** Jangan pakai "Geser →", "swipe", dan sejenisnya.
- **Sumber dan disclaimer cukup di caption**, tidak di slide, kecuali user memintanya di slide.
- **Emoji hati pakai 💗** (🤍 tidak terlihat di latar terang).
- **Pakai tanda kutip melengkung** “…”. Template mengonversinya otomatis; di caption tulis manual.
- **Satu gambar per slide.** Pemakaian ulang ilustrasi hanya untuk pasangan MITOS/FAKTA. Cover dan penutup harus beda gambar.

## Gaya ilustrasi
**Prompt dasar.** Selalu tempel di pesan pembuka, dalam bahasa Inggris:
> {{PROMPT_GAYA_ILUSTRASI}} Faceless characters (smooth face with no eyes, nose or mouth). No text, no letters, no logo, no watermark. Vertical 4:5 composition.

**Ruang kosong untuk teks.** Kalimat komposisi **wajib diambil dari `python3 konten/brand/visual/render.py <spec.json> --zones`**, yang mengukur posisi teks sebenarnya dari copy. Copy dan spec ditulis dulu, baru prompt. Jangan menulis persentase dengan tebakan.
- Pelajaran: kalimat umum seperti "left 45% and the top 30%" sering dibaca ChatGPT sebagai pojok kiri atas saja, sehingga tokoh ditaruh di kiri-bawah dan tertutup teks. Kalimat dari `--zones` sudah memakai rumusan yang tegas, termasuk aturan ukuran tokoh ("Make the characters LARGE…").
- Kalau ilustrasi sudah jadi dan tokoh ada di sisi teks: coba `veil: "none"` (kalau dinding di belakang teks polos) atau `veil: "atas"` + teks lebih ringkas; `flip: true` mencerminkan ilustrasi. Kalau tetap menabrak, minta user generate ulang dengan kalimat koreksi.

**Karakter tetap.** Sebut ciri-cirinya persis di setiap pesan pembuka supaya konsisten:
| Tokoh | Ciri |
|---|---|
| {{TOKOH_1}} | {{CIRI_TOKOH_1}} |
| {{TOKOH_2}} | {{CIRI_TOKOH_2}} |

**Larangan:**
- wajah realistis atau foto orang sungguhan
- warna neon
- teks atau huruf apa pun di ilustrasi (semua teks ditambahkan lewat template)
- logo merek lain
{{LARANGAN_TAMBAHAN}}

## Alur produksi (Rupa)
1. "Naka, siapkan visual <KODE>". Rupa menulis `spec.json` + `caption.txt`, mengukur `--zones`, lalu menulis `prompt.md`. Tilik memeriksa (titik cek 1).
2. User membuat ilustrasi di ChatGPT (satu chat, rasio 4:5). Cara cepat: `python3 konten/brand/visual/ilustrasi.py <KODE>`; helper menyalin prompt ke clipboard satu per satu dan memindahkan gambar yang diunduh ke `ilustrasi/A.png`, `B.png`, …
3. "Naka, render <KODE>". Tilik cek ilustrasi (titik cek 2) → Rupa render → Tilik cek PNG final (titik cek 3) → baru dilaporkan ke user.
