# Sumber gambar

| File | Asal | Detail | Lisensi / kredit | Tanggal |
|---|---|---|---|---|
| s02.jpg | Magnific stok | id 414311494 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/414311494) | 2026-11-20 |
| s03.jpg | Magnific stok | id 307593193 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/307593193) | 2026-11-20 |
| s04.jpg | Magnific stok | id 33377183 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/33377183) | 2026-11-20 |
| s05.jpg | Magnific stok | id 424255290 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/424255290) | 2026-11-20 |
| s06.jpg | Magnific stok | id 403127608 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/403127608) | 2026-11-20 |
| s08.jpg | Magnific stok | id 8437839 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/8437839) | 2026-11-20 |
| s09.jpg | Magnific stok | id 414172228 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/414172228) | 2026-11-20 |
| s10.jpg | Magnific stok | id 424785676 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/424785676) | 2026-11-20 |
| cover.jpg | Magnific stok | id 401555884 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/401555884) | 2026-11-20 |
| s07.jpg | Magnific stok | id 433856284 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/433856284) | 2026-11-20 |
| (cover AI) | Magnific AI (Mystic) | task becc52ed-83e7-44bc-8fda-2662caf1c2e6; ruang tamu malam, TV tabung + HP vertikal | hasil AI milik user | 2026-11-20 | tidak dipakai — generate selesai (1 kredit AI terpakai) tapi file tidak bisa diunduh: host cdn-magnific.freepik.com diblokir proxy environment |
| cover.jpg | Magnific stok | id 401555884 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/401555884) | 2026-11-20 | pengganti cover AI; layar HP putih diisi lokal dengan potongan buram gambar layar TV di foto yang sama → cover-layar.jpg, lalu dipotong 4:5 + ruang atas diperpanjang (blur cermin) → cover-crop.jpg (dipakai) |
| s07.jpg | Magnific stok | id 433856284 | lisensi Magnific (https://www.magnific.com/profile/license/pdf/433856284) | 2026-11-20 | |
| s03-ai.png | Magnific AI (Mystic) | task 493758df-71ea-4d7e-b7b1-fd3cf772e417; prompt: Realistic photo of an Indonesian family living room in the early 2000s, evening warm light. An old CRT television sits o | hasil AI milik user | 2026-11-20 |
| s03.jpg | (lihat atas) | id 307593193 | | 2026-11-20 | tidak dipakai lagi — QA Tilik: ruang tamu bergaya Barat 70-an (radiator, wallpaper bunga); diganti s03-ai.png |
| s05-layar.jpg | olahan lokal dari s05.jpg (id 424255290) | layar TV putih diisi potongan buram layar TV dari cover.jpg (id 401555884), skrip foto/layar-s05.py | lisensi kedua foto stok di atas | 2026-11-20 | QA Tilik: layar putih seperti placeholder |
| s03-ai-layar.png | olahan lokal dari s03-ai.png (task 493758df) | layar CRT polos diisi potongan buram layar TV dari cover.jpg (id 401555884) + vignette & garis scan; badge bezel & label panel kontrol palsu diburamkan; skrip foto/layar-s03.py | hasil AI milik user + lisensi Magnific 401555884 | 2026-11-20 | QA Tilik putaran 2; dipakai di slide 3 |

## Cover revisi 1 (20 Nov 2026): ElevenLabs
- `cover-el.png` (dipakai di slide 1): ElevenLabs, model `gpt-image-2.5-sunburst`, flow `8OT128ivA44tVAhRMKZB`, 4:5 2K high, 1664×2080. **471 kredit.**
- `cover-el-1.png`, `cover-el-2.png`: percobaan pertama, keluar 16:9 1K karena node belum diatur (2 × 190 = **380 kredit**), tidak dipakai.
- Total kredit ElevenLabs untuk cover ini: **851** (anggaran ± 1.000).
- Gambar AI orisinal: tanpa poster/cuplikan berhak cipta, tanpa wajah orang sungguhan, tanpa logo.
- `cover-el-layar.jpg` (dipakai di slide 1): `cover-el.png` dengan layar TV diburamkan lokal (adegan AI berwajah dihapus), tanpa kredit tambahan.

## Revisi 2 (20 Nov 2026): gambar dari tim
Sumber: **gambar dari tim (aadilah, Google Drive, 20 Nov 2026)**, feedback Discord "gambarnya pake ini dong biar lebih relate". Disediakan tim sendiri (brand.md: cuplikan film/foto disediakan user), tanpa unduhan/generate baru, tanpa kredit Magnific/ElevenLabs. Tiap slide memakai keterangan kecil "*gambar cuplikan film: <judul>" (field `kredit` di spec).

| File | Isi | Dipakai di | Olahan lokal |
|---|---|---|---|
| `tim/cover.png` → `tim/cover-blur.jpg` | poster Cinta Fitri Season 3 | slide 1 (cover, gaya `lingkar`) | area langit + judul/credit poster (y < ± 655 px) diburamkan supaya judul slide terbaca; wajah tidak disentuh |
| `tim/1.png` | poster Heart Series | slide 2 (`sisi`) | tidak ada (poster utuh) |
| `tim/2.png` → `tim/2-crop.jpg` | poster Inikah Rasanya | slide 3 (`latar`) | potong 8 px atas (sisa elemen biru di pojok) |
| `tim/3.png` | poster Kepompong | slide 4 (`polaroid`) | tidak ada (dipotong lewat `gambar_pos`) |
| `tim/4.png` | poster Cinta Terbagi 5 | slide 5 (`sisi`) | tidak ada |
| `tim/5.png` | key art Si Cecep (750×500, resolusi rendah) | slide 6 (`atas`) | tidak ada; tampil ± 1,25× sehingga agak lembut |
| `tim/6.png` → `tim/6-crop.jpg` | cuplikan Buku Harian Nayla (screenshot HP) | slide 7 (`polaroid`) | potong ikon X/share/bookmark di atas serta judul + logo "now" di bawah |

Gambar slide 1–7 sebelumnya (cover-el-layar.jpg, s02.jpg, s03-ai-layar.png, s04.jpg, s05-layar.jpg, s06.jpg, s07.jpg) tidak dipakai lagi tapi file tetap disimpan. Slide 8–10 tidak berubah.

**Koreksi QA Tilik (20 Nov 2026):** `tim/3.png` (poster Kepompong) **tidak dipakai** — poster buatan AI dengan wajah dan nama aktor sungguhan (melanggar brand.md). Slide 4 kembali memakai `s04.jpg` (Magnific, seperti sebelum revisi 2), tanpa keterangan cuplikan. Menunggu versi poster asli dari tim.
