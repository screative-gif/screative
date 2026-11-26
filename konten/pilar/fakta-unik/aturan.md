# Aturan tetap pilar Fakta Unik

Berlaku untuk semua carousel Fakta Unik, manual maupun otomatis (`otomatis/ALUR.md`). Aturan umum brand tetap berlaku: `konten/brand/brand.md` (suara & batasan) dan `konten/brand/visual.md` (warna, font, layout, kerapian).


**1. Kotak harga di slide CTA selalu sama dengan C-GAJI** (`konten/visual/2026-11-19_C-GAJI/slide-10.png`).
- Isinya (judul "Harga patungan di Seakun", 6 logo layanan + harga + "/bulan") disimpan sekali di `konten/brand/visual/brand.json` → `cta_harga`. `render.py` memasangnya otomatis di layout `cta-seakun`.
- Jangan menulis `layanan`/`judul_harga` di spec; kalau ditulis pun diabaikan. Yang boleh beda per carousel hanya kalimat jembatan, `manfaat`, dan foto latar.
- Harga berubah? Ubah `brand.json` `cta_harga` saja (atas izin user), jangan per carousel. Pengecualian hanya kalau user minta, lewat `"harga_khusus": true`.

**1b. Gaya slide CTA selalu seperti C-SINETRON** (`konten/visual/2026-11-21_C-SINETRON/slide-10.png`, keputusan user 26 Nov 2026).
- **Latar = foto yang di-blur**, bukan hijau polos. `render.py` otomatis memakai foto cover (slide 1) kalau `gambar_latar` tidak diisi, dan selalu mem-blur latar (`latar_blur`, default 12). Boleh isi `gambar_latar` dengan foto lain yang nyambung dengan topik.
- **Logo provider di kotak harga di-blur** (`logo_blur`, default 5). Jangan dimatikan kecuali user minta.
- Tombol "Kunjungi seakun.id" gaya `tap` (ikon tangan), tanpa bar footer. Keduanya sudah default; jangan menulis `tombol`, `footer`, atau `bar_kanan` di slide CTA.
- Contoh salah: slide 10 C-OJOL versi 23 Nov (latar hijau polos, tombol panah kuning, bar footer, logo tajam).

**1c. Gaya cover digilir (keputusan user 26 Nov 2026).** Cover tidak boleh monoton. Urutan: `lingkar` → `editorial` → `poster` → kembali ke `lingkar`; gaya cover selalu beda dari carousel sebelumnya.
- Sebelum membuat foto cover: `python3 konten/brand/visual/gaya_cover.py` → gaya berikutnya + arahan komposisi foto (lingkar: subjek tengah-bawah, atas kosong; editorial: subjek atas-tengah, bawah kosong; poster: subjek di kanan, kiri kosong). Prompt ElevenLabs mengikuti arahan itu.
- Spec slide 1: `"layout": "berita", "kartu": "<gaya>"`. `check.py` memberi ✗ `COVER MONOTON` kalau sama dengan cover sebelumnya.
- Contoh salah: C-SINETRON, C-REKAP, C-OJOL, C-JURUSAN (21–26 Nov) semuanya `lingkar`.

**2. Gambar: cover pakai ElevenLabs, slide lain Magnific.**
- **Cover (slide 1)**: dibuat **Naka** lewat connector ElevenLabs (`creative_generate_image`, model `gpt-image-2.5-sunburst`), lalu disimpan di `<folder>/foto/cover-el.png`. Rupa tinggal memakainya di spec slide 1.
  - Wajib set node ke **4:5, 2K, high** (`creative_update_node` → `model_parameters {"aspect_ratio":"4:5","resolution":"2K","quality":"high"}`, lalu `creative_run_flow_nodes`). Default model 16:9 1K, dan tulisan "4:5" di prompt **tidak** mengubah rasio.
  - Biaya ± 471 kredit per gambar 2K. Anggaran ± 1.000 kredit per cover → maks 2 gambar. Jangan memanggil ulang untuk "retry".
  - Prompt: foto sinematik nyata, suasana Indonesia, posisi subjek **sesuai gaya cover giliran ini** (no. 1c, dari `gaya_cover.py`), tanpa teks, tanpa logo, tanpa wajah orang sungguhan, layar TV/HP hanya cahaya buram (tanpa orang, wajah, atau tulisan). Ingat area atas ± 50% tertutup judul cover: subjek penting jangan di sana.
  - Poster/cuplikan film/sinetron berhak cipta **hanya acuan gaya** di prompt, tidak diunduh lalu di-upscale untuk diposting.
  - Catat model, flow_id, dan kredit terpakai di `foto/SUMBER.md`.
  - ElevenLabs tidak tersedia/unduhan diblokir → cadangan Magnific (`gambar.py` stok atau `ai`), sebutkan alasannya.
- **Slide 2 dst. yang menyebut nama spesifik** (judul sinetron/film, produk, tokoh, tempat, peristiwa): gambar asli dicari agent **Sidik**: **Wikipedia dulu** (`gambar.py wikipedia`, gratis), kalau tidak ada yang bagus dan sesuai baru **Google Images** via Apify (`gambar.py google`), lalu `pakai` (keputusan user 21 Nov 2026). Dipakai sebagai cuplikan pendukung, **wajib `kredit` atas nama pemilik hak** (mis. `*poster: RCTI / MNC Pictures`), tidak untuk cover, tidak di-upscale/dipotong untuk menghapus logo pemilik.
- **Slide 2 dst. bertema umum**: Magnific lewat `konten/brand/visual/gambar.py` (stok; `wiki` untuk foto faktual berlisensi, wajib kredit). Maks 1 unduhan per slide + maks 1 `ai` per carousel kalau stok tidak ada.

**3. Gambar harus menunjukkan hal yang dibahas slide itu (keputusan user 21 Nov 2026).**
- Kalau judul/isi slide menyebut nama spesifik (judul sinetron/film, acara, produk, tokoh, tempat, peristiwa), gambarnya harus **benda/judul yang sama**, bukan contoh lain yang mirip. Contoh salah: slide 2 C-SINETRON membahas sinetron *Terikat Janji*, tapi memakai poster *Heart Series*. Yang benar: poster/cuplikan *Terikat Janji*.
- Gambar untuk slide dengan nama spesifik dicari otomatis oleh **Sidik** dari Google Images. Gambar dari tim (Drive/Discord) tetap boleh dan didahulukan kalau ada; juga dicocokkan per slide dengan isinya, bukan dipasang berurutan nomor file. Kalau tidak ada gambar yang cocok untuk slide dengan nama spesifik: pakai gambar generik yang tidak menyiratkan judul lain (mis. foto suasana), lalu minta gambar yang tepat ke tim lewat Naka. Gambar bertema umum (mis. poster nostalgia) hanya untuk slide yang memang membahas hal umum (mis. "dulu TV rajanya").
- Kredit "*gambar cuplikan film: <judul>" wajib sama dengan hal yang dibahas di slide; kalau kreditnya menyebut judul yang tidak ada di teks slide, itu tanda gambarnya salah tempat.

**4. Paragraf isi penuh selebar kolom (keputusan user 21 Nov 2026).**
- Kalau gambar tidak berada di samping teks (`gambar_mode` `atas`, `latar`, `strip`, atau tanpa gambar), paragraf `isi` **tidak dipenggal manual dengan `\n`**; biarkan teks mengalir selebar kolom. Penggalan manual hanya untuk kolom sempit (`sisi`, `polaroid`, `lingkaran`).
- Saat mengganti `gambar_mode` dari mode sempit ke mode lebar, hapus semua `\n` di `isi`. Contoh salah: slide 6 C-SINETRON (mode `atas`, paragraf dipenggal 3 baris pendek, separuh kanan kosong).
- `check.py` menandai ini sebagai ✗ `KOSONG: paragraf isi dipenggal manual`.

**5. Caption tanpa sumber dan tanpa hashtag** (keputusan user 20 Nov 2026).
- Cukup pertanyaan pembuka + 1–2 paragraf singkat.
- Sumber tetap dicatat di draft, `foto/SUMBER.md`, dan baris "Sumber: …" di footer slide data.

**6. Gambar dari tim didahulukan.** Kalau tim melampirkan gambar/link di Discord, pakai itu dulu sebelum Sidik/Magnific/ElevenLabs.

**7. Di Discord, sebut topik pakai nomor emoji + judul** (1️⃣–🔟 sesuai urutan di pesan radar), bukan nomor radar.
