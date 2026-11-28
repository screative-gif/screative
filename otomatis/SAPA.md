# Sapa: soft selling lewat komentar Threads

Keputusan user 28 Nov 2026: agent mencari postingan **orang lain** di Threads soal **film/serial** (review, minta rekomendasi, list favorit, curhat abis nonton, nanya judul), menulis komentar soft selling, lalu mengirimnya dari akun **@diarydheanas** lewat Threads API. X belum (API berbayar, aturan otomasi X melarang balasan otomatis berbasis keyword).

## Aturan tetap
- **Tidak ada komentar yang terkirim tanpa ✅ anggota tim di Discord** (user di `otomatis/config.json` → `user_boleh_respon`).
- Maksimal **10 komentar/hari**, jeda 90 detik antar komentar (`otomatis/sapa.json`). Volume tinggi dari satu akun = dianggap spam oleh Meta.
- Akun @diarydheanas wajib mencantumkan "tim @seakun.id" di bio; komentar boleh menyebut seakun.id sebagai saran santai tanpa "aku dari tim" (keputusan user 28 Nov 2026, identitas di bio), tapi tidak boleh pura-pura pelanggan/penonton biasa (tanpa testimoni atau skenario karangan). seakun.id maks 1 dari 3 komentar. Jangan jalankan sebelum bio @diarydheanas mencantumkan tim @seakun.id.
- Tidak memakai bot browser (Claude in Chrome dll.) untuk mengirim komentar otomatis; otomatis hanya lewat Threads API resmi.
- Batasan `konten/brand/brand.md` berlaku penuh (nama layanan tersamar, tanpa harga, tanpa janji 100% aman).

## Alur (sesi terjadwal atau "Naka, jalankan Sapa")
1. `python3 otomatis/sapa.py cek`: token Threads OK? Gagal → kirim ke Discord "⚠️ Sapa: token Threads bermasalah", berhenti.
2. `python3 otomatis/sapa.py proses`: kirim dulu draft lama yang sudah di-✅.
3. `python3 otomatis/sapa.py cari > /tmp/sapa_kandidat.json` (± $0,1–0,2 Apify). Kandidat kosong → berhenti.
4. Panggil agent **sapa** dengan path file kandidat → dia menulis `otomatis/sapa_draft/<waktu>.json`.
5. Naka cek draft (aturan di `.claude/agents/sapa.md`), lalu `python3 otomatis/sapa.py kirim-draft otomatis/sapa_draft/<waktu>.json`.
6. Commit `otomatis/sapa_state.json` + draft ke main.

Tim di Discord (mode manual, sekarang): buka link, salin draft, komentari dari @diarydheanas, lalu ✅; ❌ = lewati.
Mode api (nanti): ✅ kirim, ❌ lewati, atau balas pesan draft dengan `ganti: <teks baru>` lalu ✅; terkirim pada `proses` berikutnya.

Usulan jadwal (belum dibuat): cari + kirim draft 09.00 WIB, `proses` 13.00 & 19.00 WIB. Hemat Apify: 1 pencarian/hari ≈ $3–6/bulan, jadi pertimbangkan 3x seminggu supaya jatah $5 cukup juga untuk riset.

## Setup
- Network secret `graph.threads.net`: header `Authorization`, prefix `Bearer`, value = long-lived token Threads @diarydheanas (dari app Meta Rekafin → Threads API → User Token Generator). Izin minimal: `threads_basic`, `threads_content_publish`, `threads_manage_replies`. Token berlaku 60 hari: refresh sebelum habis. **Reset app secret membuat token lama mati.**
- `threads_keyword_search` tidak dipakai (tanpa Advanced access hanya mengembalikan post sendiri); pencarian lewat Apify `scrapesage/threads-search-scraper`.
- **Diuji 28 Nov 2026: `postId` dari Apify DITOLAK sebagai `reply_to_id`** ("not a valid threads_media ID"). Membalas post orang lain lewat API butuh ID media Graph, yang hanya didapat lewat `threads_keyword_search` (Advanced access, perlu app review). Sampai review lolos, `mode_kirim` = `manual`: tim membuka link di Discord, mengomentari sendiri dari @diarydheanas, lalu ✅; `proses` hanya mencatat. Setelah lolos: ganti `mode_kirim` ke `api` dan ganti pencarian ke keyword_search API.
