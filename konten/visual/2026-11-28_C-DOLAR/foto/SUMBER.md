# Sumber gambar C-DOLAR

## Cover (slide 1): ElevenLabs
- `cover-el.png`: ElevenLabs, model `gpt-image-2.5-sunburst`, flow `RCaUhLkTDZ7YihuHuYy7`, generation `QlRXrMTMAzQf6QhVzEAk`, 4:5 2K high (node diatur sebelum jalan), 1664×2080, **471 kredit** (total kredit ElevenLabs carousel ini: 471). Gaya cover: **poster** (dari `gaya_cover.py`, setelah editorial C-JURUSAN).
- Isi: gerobak gorengan malam di gang basah Jakarta, di kanan: nampan gorengan, mi instan polos tanpa merek, toples kedelai, tangan (tanpa wajah) memegang uang rupiah + dolar. Kiri ± 50% jalan gelap buram (ruang judul). Tanpa teks, logo, wajah.

## Slide 2, 4, 5, 6, 8: Rupa (Magnific stok GAGAL, 28 Nov 2026)
- `cari` (gratis) jalan, kandidat dipilih: s2 id 23856390 (papan angka digital buram), s4 id 36002151 (bakwan di serok), s5 id 18293883 (tempe + kedelai mentah), s6 id 2892645 (obat strip di meja), s8 id 135419357 (tangan pedagang menata cabai, tanpa wajah).
- `unduh` ditolak API Magnific: HTTP 403 `{"message":"Tool not allowed for enterprise account."}` untuk semua id (termasuk id 64045357 yang berhasil diunduh 26 Nov). `ai` (Mystic) juga 403 (1 percobaan, tidak ada gambar yang dibuat). Wikimedia/Wikipedia: 429.
- **Kredit Magnific terpakai: 0 unduhan, 0 generate.** Tidak ada file gambar baru; slide 2, 4, 5, 6, 8 dirender tanpa foto (visual data di latar kertas).
- Slide 10 (CTA): latar = `cover-el.png` di-blur (default render.py).
