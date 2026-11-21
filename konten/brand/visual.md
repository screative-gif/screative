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
- **Cover = layout `berita`, kotak headline default `kartu: "kaca"` (disetujui user 2026-11-19):** foto full-bleed, panel kaca buram keputihan (blur + garis putih tipis), label oranye **miring** menempel di tepi atas panel (`kicker`, mis. REKOMENDASI TONTONAN), judul putih tebal, **hook** (`__teks__`) teks hijau mint #7AEBD6 dengan stabilo oranye tipis di separuh bawah huruf (seperti stabilo desain stiker), subjudul putih regular. Varian lain tetap tersedia lewat `kartu`: `klasik` (kartu putih + strip), `stiker`, `pita`, `gradasi`, `tiket` (tiket bioskop hijau tua, garis sobekan + logo), `neo` (kotak mint, garis hitam tebal + bayangan keras), `strip` (setiap baris judul di pita hijau tua, sedikit miring). **Headline tipografi** (tanpa kotak, teks besar langsung di foto): `lingkar` (judul putih tebal di atas, kata hook dilingkari coretan oranye; tombol kaca `ajakan` + panah hanya kalau diisi, default tidak ada), `editorial` (baris 1 sans kecil, baris tengah serif italic besar Instrument Serif, hook di kotak oranye miring, subjudul huruf kapital renggang), `poster` (huruf condensed Anton kapital raksasa, hook mint, label sobek oranye di atas + label sobek putih untuk subjudul). Baris judul dipecah manual dengan `\n`.
### Pilihan cover format berita (keputusan user 2026-11-19)
Cover format berita **hanya memakai 3 gaya tipografi: `lingkar` (H), `editorial` (I), `poster` (J)**. Rupa memilih per cover supaya **subjek utama foto tetap terlihat** (wajah/tokoh/objek tidak tertutup teks):
| Posisi subjek di foto cover | Gaya | Alasan |
|---|---|---|
| Subjek di tengah–bawah, area atas relatif kosong (langit, dinding, latar gelap) | `lingkar` | teks di sepertiga atas, gradasi gelap hanya di atas |
| Subjek di atas–tengah, area bawah relatif kosong/tenang | `editorial` | teks di sepertiga bawah, gradasi gelap hanya di bawah |
| Subjek di sisi kanan, sisi kiri relatif kosong; atau hook sangat pendek & provokatif | `poster` | teks rata kiri, huruf condensed sempit; geser foto (`foto_pos`) supaya subjek ke kanan |
- Kalau ragu, render 2 gaya dan pilih yang wajah/subjeknya paling utuh; sebutkan alasan pilihan di laporan.
- Jangan menaruh teks di atas wajah. Atur `foto_pos` (mis. `"center 70%"`) sebelum mengganti gaya.
- Gaya lama (`kaca`, `klasik`, `stiker`, `pita`, `gradasi`, `tiket`, `neo`, `strip`) tetap ada di template, tapi tidak dipakai untuk cover kecuali user memintanya.
- **Slide data = layout `data`** (format "cerita di balik", lihat `formula-carousel.md`; revisi user 19 Nov 2026): **tanpa label kecil & tanpa nomor halaman**, **gambar di atas** (`gambar`, wajib di setiap slide kalau tersedia), judul 2 baris (`__teks__` hijau tua + **stabilo oranye**; semua stabilo oranye), isi singkat, **1 visual data** (`angka-besar`, `batang`, `dulu-vs-sekarang`, `tabel`, `daftar`, `kutipan`, `notif` untuk slide kejutan), kalimat penutup tebal. **Sumber tampil di tengah bar footer** ("Sumber: …", isi field `sumber`, singkat 1 baris). Bar footer otomatis versi padat. Dengan gambar, ruang visual data lebih sempit: maks 3 batang / 4 baris tabel / 5 notif. **Slide CTA = layout `cta-seakun`** (hijau tua, kalimat jembatan, kotak harga baku C-GAJI dari `brand.json` `cta_harga`, tombol Kunjungi seakun.id, `bar_kanan: "ig"`).
- **Variasi wajib slide data (revisi user 20 Nov 2026):**
  - Setiap slide **menyorot 1 pesan utama**; sisanya pendukung. Perbandingan angka → `versus` (kartu + panah + badge selisih) atau `balapan` (batang + **garis acuan** + anotasi). Penurunan → `turun` (angka besar + panah) atau `kolom` (kolom vertikal, selisih ditulis di kolom yang disorot). Satu angka besar + pendukung → `kartu-angka`. Notif HP: item penting diberi `sorot: true`. Selalu beri **label, panah, atau anotasi** yang menjelaskan perbandingannya.
  - Gambar pendukung dibuat **kecil** (`gambar_mode`: `polaroid`, `lingkaran`, `sisi`, `strip` + `gambar_label`). Gambar besar (`atas`, `latar`) hanya kalau gambarnya ikut membawa pesan. **Jangan pakai mode gambar & jenis visual yang sama di 2 slide berurutan.**
  - **Palet:** utama `#09A185`, sekunder `#4EE77D`, highlight `#FF4F2F`, highlight lain `#FAD02C` (boleh turunan satu palet). Grafik **maks 2 warna**: pembanding = hijau utama, yang disorot = `#FF4F2F`.
  - **Highlight:** judul/penutup `__teks__` = pil kuning `#FAD02C`; **tanda baca di ujung ikut masuk pil** ("naik kok."); tanpa coretan/aksen. Isi `==teks==` = pil hijau muda; isi `__teks__` = pil hijau utama teks putih (angka terpenting).
  - **Font:** judul Poppins Bold; semua teks lain **Open Sauce Sans Medium** (tebal: Open Sauce Sans Bold).
  - **Bar footer:** kaca hijau bergradasi (`#09A185` → `#4EE77D`, opasitas ±0,9 → 0,7 di latar kertas), **semua teks putih**, tombol panah bulat putih transparan (versi disetujui user 20 Nov).
  - **`penutup` hanya kalau menambah insight/fakta baru** (mis. "UMP DKI 2026 sendiri naik 6,17% dari 2025."). Jangan pakai kalimat jargon yang mirip di tiap slide; kalau tidak ada insight tambahan, kosongkan. Jarak penutup ke bar footer dibuat lega (otomatis).
  - Mode `latar`: foto penuh di atas (sudut bawah membulat), judul putih di atas foto, header otomatis putih. Teks di atas foto **tidak boleh mepet tepi bawah foto**: atur `gambar_tinggi` (± 740) & `teks_dalam` (± 330). Highlight tanpa bayangan teks.
  - **Highlight hemat:** maksimal **1 highlight per kalimat/judul**, pilih angka/frasa terpenting. Pil kuning dibuat rapat (padding atas-bawah kecil).
  - **Judul yang berakhir dengan %, ?, atau simbol lain tidak diberi titik lagi.**
  - **Kalimat penjelas grafik** (catatan di bawah `versus`, `anotasi` balapan, label garis acuan): **1 warna saja per kalimat** (hijau utama atau `#FF4F2F`), tanpa pil/kotak, tanpa campuran warna.
  - **Bagan maks 3 warna termasuk putih**: putih + hijau utama + `#FF4F2F`. Kuning hanya untuk pil highlight teks, bukan di bagan.
  - **Slide tanpa sumber data** (mis. angka ilustrasi, penutup): kosongkan `sumber`, bagian tengah footer dibiarkan kosong. Angka ilustrasi diberi catatan kecil di bawah visualnya (`visual.catatan`: "Note: angka simulasi").
  - Teks di dalam kotak/kartu minimal 26 px; ringkas keterangannya supaya cukup 1–2 baris.
  - **Acuan yang sudah disetujui user:** slide 2–4 C-GAJI (spec: `konten/brand/visual/contoh/data-variasi.json`): versus + polaroid, balapan + strip bahan pokok berlabel, turun + latar. Tiru tingkat kerapiannya untuk slide lain.
- **Slide isi = layout `berita-isi`:** foto di atas (± 700 px), lalu 2–3 paragraf pendek di latar kertas; `**tebal**`, `__hijau__`.
- **Bar bawah (`footer: "bar"`, otomatis):** pil kaca (glassmorphic: hijau transparan + blur + garis putih tipis), kecil: seakun.id | Hemat • Aman • Legal | Geser ›. Lebar bar sejajar kotak headline (kiri-kanan 56 px). Teks tengah bisa diganti per slide lewat `bar_tengah` (list). **Slide terakhir wajib `bar_kanan: "ig"`** (ikon Instagram + @seakun.id, tanpa "Geser"). Pengecualian dari aturan "Tanpa CTA geser": khusus format berita, disetujui user. Tagline hanya di header (kecil).
- Contoh spec: `konten/brand/visual/contoh/berita.json`.

## Aturan tetap carousel berita / "cerita di balik" (keputusan user 20 Nov 2026)
Berlaku untuk semua carousel format berita/data berikutnya, manual maupun otomatis (`otomatis/ALUR.md`).

**1. Kotak harga di slide CTA selalu sama dengan C-GAJI** (`konten/visual/2026-11-19_C-GAJI/slide-10.png`).
- Isinya (judul "Harga patungan di Seakun", 6 logo layanan + harga + "/bulan") disimpan sekali di `konten/brand/visual/brand.json` → `cta_harga`. `render.py` memasangnya otomatis di layout `cta-seakun`.
- Jangan menulis `layanan`/`judul_harga` di spec; kalau ditulis pun diabaikan. Yang boleh beda per carousel hanya kalimat jembatan, `manfaat`, dan foto latar.
- Harga berubah? Ubah `brand.json` `cta_harga` saja (atas izin user), jangan per carousel. Pengecualian hanya kalau user minta, lewat `"harga_khusus": true`.

**2. Gambar: cover pakai ElevenLabs, slide lain Magnific.**
- **Cover (slide 1)**: dibuat **Naka** lewat connector ElevenLabs (`creative_generate_image`, model `gpt-image-2.5-sunburst`), lalu disimpan di `<folder>/foto/cover-el.png`. Rupa tinggal memakainya di spec slide 1.
  - Wajib set node ke **4:5, 2K, high** (`creative_update_node` → `model_parameters {"aspect_ratio":"4:5","resolution":"2K","quality":"high"}`, lalu `creative_run_flow_nodes`). Default model 16:9 1K, dan tulisan "4:5" di prompt **tidak** mengubah rasio.
  - Biaya ± 471 kredit per gambar 2K. Anggaran ± 1.000 kredit per cover → maks 2 gambar. Jangan memanggil ulang untuk "retry".
  - Prompt: foto sinematik nyata, suasana Indonesia, subjek di bagian bawah/tengah-bawah (atas dipakai judul), tanpa teks, tanpa logo, tanpa wajah orang sungguhan, layar TV/HP hanya cahaya buram (tanpa orang, wajah, atau tulisan). Ingat area atas ± 50% tertutup judul cover: subjek penting jangan di sana.
  - Poster/cuplikan film/sinetron berhak cipta **hanya acuan gaya** di prompt, tidak diunduh lalu di-upscale untuk diposting.
  - Catat model, flow_id, dan kredit terpakai di `foto/SUMBER.md`.
  - ElevenLabs tidak tersedia/unduhan diblokir → cadangan Magnific (`gambar.py` stok atau `ai`), sebutkan alasannya.
- **Slide 2 dst. yang menyebut nama spesifik** (judul sinetron/film, produk, tokoh, tempat, peristiwa): gambar asli dari **Google Images, dicari agent Sidik** (`gambar.py google` lalu `pakai`; keputusan user 21 Nov 2026). Dipakai sebagai cuplikan pendukung, **wajib `kredit` atas nama pemilik hak** (mis. `*poster: RCTI / MNC Pictures`), tidak untuk cover, tidak di-upscale/dipotong untuk menghapus logo pemilik.
- **Slide 2 dst. bertema umum**: Magnific lewat `konten/brand/visual/gambar.py` (stok; `wiki` untuk foto faktual berlisensi, wajib kredit). Maks 1 unduhan per slide + maks 1 `ai` per carousel kalau stok tidak ada.

**3. Gambar harus menunjukkan hal yang dibahas slide itu (keputusan user 21 Nov 2026).**
- Kalau judul/isi slide menyebut nama spesifik (judul sinetron/film, acara, produk, tokoh, tempat, peristiwa), gambarnya harus **benda/judul yang sama**, bukan contoh lain yang mirip. Contoh salah: slide 2 C-SINETRON membahas sinetron *Terikat Janji*, tapi memakai poster *Heart Series*. Yang benar: poster/cuplikan *Terikat Janji*.
- Gambar untuk slide dengan nama spesifik dicari otomatis oleh **Sidik** dari Google Images. Gambar dari tim (Drive/Discord) tetap boleh dan didahulukan kalau ada; juga dicocokkan per slide dengan isinya, bukan dipasang berurutan nomor file. Kalau tidak ada gambar yang cocok untuk slide dengan nama spesifik: pakai gambar generik yang tidak menyiratkan judul lain (mis. foto suasana), lalu minta gambar yang tepat ke tim lewat Naka. Gambar bertema umum (mis. poster nostalgia) hanya untuk slide yang memang membahas hal umum (mis. "dulu TV rajanya").
- Kredit "*gambar cuplikan film: <judul>" wajib sama dengan hal yang dibahas di slide; kalau kreditnya menyebut judul yang tidak ada di teks slide, itu tanda gambarnya salah tempat.

**4. Paragraf isi penuh selebar kolom (keputusan user 21 Nov 2026).**
- Kalau gambar tidak berada di samping teks (`gambar_mode` `atas`, `latar`, `strip`, atau tanpa gambar), paragraf `isi` **tidak dipenggal manual dengan `\n`**; biarkan teks mengalir selebar kolom. Penggalan manual hanya untuk kolom sempit (`sisi`, `polaroid`, `lingkaran`).
- Saat mengganti `gambar_mode` dari mode sempit ke mode lebar, hapus semua `\n` di `isi`. Contoh salah: slide 6 C-SINETRON (mode `atas`, paragraf dipenggal 3 baris pendek, separuh kanan kosong).
- `check.py` menandai ini sebagai ✗ `KOSONG: paragraf isi dipenggal manual`.

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
- **Sumber tidak ditulis di caption, dan caption tanpa hashtag** (keputusan user 20 Nov 2026). Sumber cukup di footer slide data ("Sumber: …"), draft, dan `foto/SUMBER.md`.
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
