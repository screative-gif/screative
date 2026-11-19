# Panduan Visual Seakun (Instagram @seakun.id)

*Rupa dan Tilik wajib membaca file ini sebelum membuat atau memeriksa visual. Identitas teknis (warna, font, logo, tagline, footer) ada di `konten/brand/visual/brand.json` dan dipakai otomatis oleh `render.py`.*

## Aset
| Aset | Lokasi |
|---|---|
| Logo untuk header (kiri atas) | `konten/brand/visual/logo/seakun-logo.png` |
| Logo putih/terang untuk label footer | `konten/brand/visual/logo/seakun-logo-putih.png` |
| Font judul | Poppins Bold (`konten/brand/visual/font/Poppins-Bold.ttf`) |
| Font teks | Poppins (Regular/Medium/SemiBold/Bold) (`konten/brand/visual/font/`) |
| Contoh post brand | `konten/brand/visual/referensi/` |
| Identitas brand untuk template | `konten/brand/visual/brand.json` |
| Mesin render | `konten/brand/visual/render.py` (spec JSON jadi PNG 1080×1350) |
| Cek QA otomatis | `konten/brand/visual/check.py` (orphan, stabilo, tepi, tabrakan teks dengan tokoh, veil, area kosong, gaya). Dipakai Rupa dan Tilik |
| Helper ilustrasi ChatGPT | `konten/brand/visual/ilustrasi.py` (salin prompt ke clipboard, pindahkan hasil unduhan) |

## Warna
| Peran (di brand.json) | Hex | Dipakai untuk |
|---|---|---|
| `primary` | `#08A081` | judul, label footer, kata yang ditekankan (`**teks**`), nomor judul |
| `secondary` | `#4AD1B9` | garis putus-putus, bingkai kotak MITOS |
| `accent` / `accent_dark` | `#DD6200` / `#D45A00` | kata kunci di judul (`__teks__`), ikon, kotak FAKTA, garis pemisah |
| `highlight` | `#AAFFEF` | stabilo kata kunci (`==teks==`) |
| `text` | `#111111` | teks isi |

Latar (`backgrounds` di brand.json) selalu **lembut/pucat**: #F0F1F2, #F3F5F5, #EAF6F2. Jangan memakai warna jenuh untuk area besar.

## Format carousel Seakun (default, disetujui user 2026-11-19)
Semua slide memakai **latar kertas kusut** (`latar/kertas.jpg`), **badge logo bulat** "PLATFORM PATUNGAN #1 · seakun.id" di kiri atas, dan **titik nomor slide** (5 lingkaran hijau bertumpuk, angka = nomor slide) di kanan atas. Ini diatur `header_style: "seakun"` di brand.json.
- **Slide isi = layout `foto-atas`:** foto/cuplikan (disediakan user) di atas memudar ke latar, lalu kotak judul oranye `#FF4F2F` teks putih ("1. Pablo Escobar"), subjudul tebal (`__Judul Series__` hijau + tahun hitam), lalu isi rata kanan-kiri ± 40–60 kata.
- **Label bawah setiap slide:** "Kunjungi website **seakun.id**" (pil putih + pil hijau), `footer: "kunjungi"` (default).
- Aturan lama soal footer kanan-bawah & tagline kanan-atas di bawah ini tidak berlaku untuk format ini.

## Format carousel "berita" (alternatif, 2026-11-19)
Terinspirasi format portal berita, dimodifikasi untuk Seakun.
- **Header tengah atas:** logo Seakun putih + tagline "— PLATFORM PATUNGAN NO.1 INDONESIA —" (gradasi gelap tipis di atas foto).
- **Cover = layout `berita`:** foto full-bleed, kartu putih (sudut kanan-bawah membulat) dengan strip 3 warna hijau di atasnya, label oranye (`kicker`, mis. REKOMENDASI TONTONAN), judul tebal hitam (`__teks__` = hijau), subjudul regular.
- **Slide isi = layout `berita-isi`:** foto di atas (± 700 px), lalu 2–3 paragraf pendek di latar kertas; `**tebal**`, `__hijau__`.
- **Bar bawah (`footer: "bar"`, otomatis):** pil kaca (glassmorphic: hijau transparan + blur + garis putih tipis), kecil: seakun.id | Hemat • Aman • Legal | @seakun.id. Teks tengah bisa diganti per slide lewat `bar_tengah` (list). Tidak ada "Swipe". Tagline hanya di header (kecil).
- Contoh spec: `konten/brand/visual/contoh/berita.json`.

## Layout wajib (setiap post)
1. **Kiri atas:** logo brand
2. **Kanan atas:** tagline brand (dari brand.json). Jangan diganti tanpa izin user.
3. **Kanan bawah:** label warna primer yang menempel ke tepi kanan, berisi 🌐 seakun.id | Instagram @seakun.id
   - Varian untuk quote atau kutipan: label berisi logo putih | @seakun.id, tanpa header (`footer: "logo-ig"`, `header: false`)

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
> Flat vector illustration in a clean modern Indonesian lifestyle style, simple shapes with soft shading, warm natural skin tones, casual outfits in mustard yellow, orange and dark green, light grey paper-textured background with mint-green and teal accents, generic smartphones, tablets, headphones and popcorn as props (no real app logos). Faceless characters (smooth face with no eyes, nose or mouth). No text, no letters, no logo, no watermark. Vertical 4:5 composition.

**Ruang kosong untuk teks.** Kalimat komposisi **wajib diambil dari `python3 konten/brand/visual/render.py <spec.json> --zones`**, yang mengukur posisi teks sebenarnya dari copy. Copy dan spec ditulis dulu, baru prompt. Jangan menulis persentase dengan tebakan.
- Pelajaran: kalimat umum seperti "left 45% and the top 30%" sering dibaca ChatGPT sebagai pojok kiri atas saja, sehingga tokoh ditaruh di kiri-bawah dan tertutup teks. Kalimat dari `--zones` sudah memakai rumusan yang tegas, termasuk aturan ukuran tokoh ("Make the characters LARGE…").
- Kalau ilustrasi sudah jadi dan tokoh ada di sisi teks: coba `veil: "none"` (kalau dinding di belakang teks polos) atau `veil: "atas"` + teks lebih ringkas; `flip: true` mencerminkan ilustrasi. Kalau tetap menabrak, minta user generate ulang dengan kalimat koreksi.

**Karakter tetap.** Sebut ciri-cirinya persis di setiap pesan pembuka supaya konsisten:
| Tokoh | Ciri |
|---|---|
| Raka | pria muda ± 25 tahun, rambut hitam ikal tebal, berjenggot tipis, kaos lengan panjang kuning mustard, celana panjang hijau tua, sneakers putih |
| Nadia | perempuan muda ± 22 tahun, rambut hitam sebahu lurus, hoodie hijau mint, celana jeans biru, sneakers putih, sering memegang HP |

**Larangan:**
- wajah realistis atau foto orang sungguhan
- warna neon
- teks atau huruf apa pun di ilustrasi (semua teks ditambahkan lewat template)
- logo merek lain
- logo atau ikon resmi layanan lain (Netflix, Spotify, YouTube, dll) — pakai ikon generik
- uang tunai bertumpuk atau simbol judi/pinjol

## Alur produksi (Rupa)
1. "Naka, siapkan visual <KODE>". Rupa menulis `spec.json` + `caption.txt`, mengukur `--zones`, lalu menulis `prompt.md`. Tilik memeriksa (titik cek 1).
2. User membuat ilustrasi di ChatGPT (satu chat, rasio 4:5). Cara cepat: `python3 konten/brand/visual/ilustrasi.py <KODE>`; helper menyalin prompt ke clipboard satu per satu dan memindahkan gambar yang diunduh ke `ilustrasi/A.png`, `B.png`, …
3. "Naka, render <KODE>". Tilik cek ilustrasi (titik cek 2) → Rupa render → Tilik cek PNG final (titik cek 3) → baru dilaporkan ke user.
