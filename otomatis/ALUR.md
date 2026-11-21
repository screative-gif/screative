# Alur otomatis carousel pilar 2 via Discord

Panduan untuk **Naka di sesi cloud terjadwal**. Setiap sesi terjadwal mulai dari nol (repo baru di-clone, tanpa ingatan), jadi semua langkah dan state ada di sini dan di `otomatis/state.json`.

- Produksi: **Senin & Jumat**. Posting: **Selasa & Sabtu**. Semua jam WIB (Asia/Jakarta, UTC+7).
- Channel, user yang boleh respon, dan jadwal: `otomatis/config.json`. Respon orang lain **diabaikan** (skrip sudah menyaring).
- Semua komunikasi ke tim lewat `python3 otomatis/discord.py …` (bot). Tidak ada orang yang membaca sesi ini, jadi **semua kabar penting (termasuk kegagalan) dikirim ke Discord**, singkat dan dalam Bahasa Indonesia santai.
- Jangan pernah mencetak token (Discord, Apify, Magnific). Token disisipkan oleh network secret environment, bukan file.

## 0. Persiapan di setiap sesi (wajib, sebelum langkah lain)
```bash
git fetch origin main otomatis/carousel 2>/dev/null
if git rev-parse --verify -q origin/otomatis/carousel >/dev/null; then
  git checkout -B otomatis/carousel origin/otomatis/carousel && git merge --no-edit origin/main
else
  git checkout -B otomatis/carousel origin/main
fi
python3 otomatis/discord.py cek
```
- Branch kerja **`otomatis/carousel`** (izin user: semua hasil otomatis di-commit & push ke branch ini, bukan ke `main`).
- Kalau `cek` gagal (401/403/tunnel 403): bot belum siap. Berhenti; tidak ada yang bisa dikirim. Tulis ringkasan error di akhir sesi.
- Di akhir setiap sesi yang mengubah file: `git add -A otomatis konten && git commit -m "…" && git push -u origin otomatis/carousel` (ulang sampai 4× kalau jaringan gagal).
- Lalu **langsung bawa ke `main`** (aturan user 21 Nov 2026: semua update harus ada di main tanpa menunggu konfirmasi): `git fetch origin main && git merge --no-edit origin/main && git push origin HEAD:main` (lalu push lagi ke `otomatis/carousel`). Kalau push ke main ditolak karena main berubah, ulangi fetch + merge + push. Kalau ada konflik yang tidak jelas, jangan paksa: tulis ke Discord bahwa hasil ada di branch `otomatis/carousel` dan belum masuk main.

## A. Kirim topik (Senin & Jumat, mulai ± 06.35, target terkirim ± 07.00)
1. `SIKLUS=$(TZ=Asia/Jakarta date +%F)`. Kalau `python3 otomatis/discord.py status --siklus $SIKLUS` sudah punya `pesan_topik`, **berhenti** (sudah terkirim).
2. Radar topik:
   - Kalau `konten/laporan/$SIKLUS_radar-topik.md` sudah ada, pakai itu.
   - Kalau belum: panggil **Sera** (radar saja: `trends.py` + `APIFY_LEWAT_PROXY=1 python3 collect.py --only ig_akun` + `analyze.py`, ± $0,2) → **Lira** tulis `konten/laporan/$SIKLUS_radar-topik.md` (10 topik + skor, format tabel sama dengan radar sebelumnya). Beri tahu Lira topik yang **sudah dipakai** (lihat `terpilih` di `otomatis/state.json` dan folder `konten/visual/`) supaya tidak diulang, dan kalender pemicu 2 minggu ke depan.
   - Kalau Sera gagal (mis. kredit Apify < $1 atau host ditolak): Lira tetap menulis radar dari Google Trends + topik radar sebelumnya yang belum dipakai + cadangan, dan menulis keyakinan "rendah". Kalau semuanya gagal, kirim ke Discord: radar gagal dibuat + alasannya, lalu berhenti.
3. `python3 otomatis/discord.py kirim-topik konten/laporan/${SIKLUS}_radar-topik.md --siklus $SIKLUS`
4. Commit + push.

## B. Eksekusi (Senin & Jumat, 10.00)
1. Ambil siklus hari ini. Kalau status bukan `menunggu-pilihan`, berhenti.
2. `python3 otomatis/discord.py baca-pilihan` → JSON. Putuskan:
   - `usulan` (balasan "usul: …") dari user yang boleh → pakai usulan terbaru, **asal lolos batasan** `konten/brand/brand.md` + aturan wajib `formula-carousel.md`. Kalau tidak lolos, pakai pilihan berikutnya dan jelaskan alasannya di Discord dengan sopan.
   - Baca juga `komentar_lain`: pilihan dalam kata-kata ("nomor 3 aja") dihitung seperti suara.
   - Suara terbanyak (seri → bobot lebih tinggi). Tidak ada respon → **bobot tertinggi** (`keputusan_otomatis`).
3. Buat KODE `C-<SATU-KATA-KUNCI>` (huruf besar, mis. `C-HARBOLNAS`) dan folder `konten/visual/<tanggal posting>_<KODE>/` (tanggal posting = besoknya: Selasa/Sabtu).
   `python3 otomatis/discord.py tandai --status produksi --terpilih '{"judul":"…","cara":"…","kode":"C-…","folder":"konten/visual/…"}'`
   `python3 otomatis/discord.py kirim "🗳️ Topik terpilih: **…** (alasan singkat: suara tim / usulan X / bobot tertinggi). Carousel lagi dikerjakan, hasilnya aku kirim ke sini."`
4. Produksi (sama dengan alur manual di `CLAUDE.md`, dengan penyesuaian mode otomatis):
   - **Riset fakta oleh Naka** (WebSearch/WebFetch): kumpulkan angka & tanggal bersumber untuk "Data yang perlu dicari" di baris radar. Simpan catatan sumber di draft. Jangan mengarang angka; yang tidak terverifikasi ditandai `[CEK FAKTA]` lalu dibuang atau diganti sebelum render final.
   - **Diksa** → `konten/draft/<tanggal posting>_<slug>.md` (wajib baca `brand.md` + `formula-carousel.md`; contoh lulus: `konten/draft/2026-11-19_gaji-naik-pas-pasan.md`).
   - **Rupa, mode otomatis**: format berita/data seperti C-GAJI (`konten/visual/2026-11-19_C-GAJI/spec.json`), **tidak menunggu ilustrasi ChatGPT dari user**. Wajib baca `visual.md`, `brand.md`, `formula-carousel.md`. Hasil: `slide-*.png` + `caption.txt` (**tanpa sumber & tanpa hashtag**) + `spec.json` + `foto/SUMBER.md`.
     - **Cover (slide 1) → ElevenLabs, dibuat Naka** (aturan tetap di `konten/brand/visual.md` → "Aturan tetap carousel berita"), anggaran **± 1.000 kredit per cover**:
       1. `creative_generate_image` model `gpt-image-2.5-sunburst`, `generations_count` 1. Prompt: foto sinematik nyata suasana Indonesia, subjek di bawah/tengah-bawah (atas ± 50% tertutup judul), layar TV/HP hanya cahaya buram tanpa orang, **tanpa teks, tanpa logo, tanpa wajah orang sungguhan**. Poster/cuplikan berhak cipta hanya acuan gaya di prompt.
       2. Panggilan pertama keluar 16:9 1K (default, ± 190 kredit). Jangan pakai hasil itu untuk cover: langsung `creative_update_node` (node dari hasil tadi) `model_parameters {"aspect_ratio":"4:5","resolution":"2K","quality":"high"}` lalu `creative_run_flow_nodes` (± 471 kredit). Kalau node bisa diatur sebelum jalan (buat flow + node dulu), lakukan itu supaya hanya bayar 1× 2K.
       3. Tunggu `creative_get_flow_run_status`, unduh `content_url` ke `<folder>/foto/cover-el.png` (host `elevenlabsusercontent.com`), lihat hasilnya.
       4. Total maks ± 1.000 kredit; jangan memanggil ulang untuk "retry". Catat model, flow_id, kredit (`price.credits` tiap generation) di `foto/SUMBER.md` dan di pesan Discord saat kirim hasil.
       5. Kalau tool ElevenLabs tidak tersedia di sesi ini atau unduhan diblokir proxy, pakai `gambar.py ai`/stok Magnific untuk cover, dan sebutkan alasannya + host yang diblokir di pesan Discord.
     - **Slide CTA**: kotak harga otomatis dari `brand.json` `cta_harga` (desain C-GAJI). Jangan menulis `layanan` di spec.
     - **Slide 2 dst. → Magnific** lewat `konten/brand/visual/gambar.py` (stok, `wiki` untuk foto faktual). Izin kredit Magnific: maks 1 unduhan per slide + maks 1 generate `ai` (hanya kalau stok tidak ada).
   - **Tilik titik cek 3** pada PNG final (+ cek 2 pada foto yang diunduh). Temuan → Rupa perbaiki → Tilik lagi, maks 3 putaran.
   - Versi Canva: kalau `konten/brand/visual/canva.py` ada, `python3 konten/brand/visual/canva.py <folder>/spec.json`.
   - `echo "MENUNGGU REVIEW $(TZ=Asia/Jakarta date +%F) (Discord)" > <folder>/STATUS.txt`
5. `python3 otomatis/discord.py kirim-hasil <folder>` (slide, caption, PDF Canva, pesan review dengan ✅).
   Kalau masih ada temuan Tilik yang belum beres setelah 3 putaran, tetap kirim dengan `--catatan "⚠️ Catatan QA: …"`.
6. Commit + push. Kalau produksi gagal di tengah jalan: `tandai --status gagal`, kirim ke Discord apa yang gagal dan apa yang dibutuhkan, commit yang sudah jadi.

## C. Cek feedback (Senin & Jumat 12.00/15.00/18.00/21.00, Selasa & Sabtu 08.00)
1. Cari siklus terbaru dengan status `menunggu-review` atau `revisi` (`python3 otomatis/discord.py status`). Kalau tidak ada, **berhenti tanpa mengirim apa pun**.
2. `python3 otomatis/discord.py baca-feedback` → JSON.
3. Ada `feedback_baru` → **revisi dulu** (feedback menang atas ✅ yang lebih lama):
   - `tandai --status revisi`. Kirim: "📝 Feedback diterima dari …, lagi aku kerjakan."
   - Teruskan poin feedback **apa adanya** ke Rupa (visual) atau Diksa (isi teks/angka; lalu Rupa render ulang) → Tilik titik cek 3 → canva.py lagi.
   - Lampiran gambar dari tim (URL `cdn.discordapp.com`) boleh diunduh ke `<folder>/foto/` kalau diminta dipakai.
   - Kalau feedback tidak jelas atau melanggar batasan brand, tanyakan balik di Discord (`kirim "…" --balas <id pesan>`) dan jangan menebak.
   - `kirim-hasil <folder> --revisi <N+1> --catatan "Yang diubah: …"`, lalu `tandai --feedback <id1,id2,…>`.
4. Tidak ada feedback baru dan ada `approve` (✅) atau `approve_lewat_teks` → **APPROVED**:
   - `echo "APPROVED $(TZ=Asia/Jakarta date +%F) (Discord: <nama>)" > <folder>/STATUS.txt`, `tandai --status approved`.
   - Kirim: "✅ Approved oleh …. Tayang otomatis di IG @seakun.id <Selasa/Sabtu> jam <jam_posting di config.json> WIB."
5. Tidak ada apa-apa:
   - Sesi 08.00 di hari posting dan status masih `menunggu-review` → kirim pengingat singkat ("Carousel hari ini belum di-approve, tolong cek ya 🙏").
   - Selain itu, berhenti tanpa mengirim apa pun.
6. Commit + push kalau ada perubahan.

## D. Posting ke Instagram (Selasa & Sabtu, jam `jadwal.jam_posting` di `config.json`)
1. Persiapan langkah 0, lalu `python3 otomatis/instagram.py cek` (token + kuota). Gagal (401/190/tunnel 403) → kirim ke Discord "⚠️ Posting IG gagal: token/akses Meta bermasalah (…)", berhenti.
2. Cari siklus terbaru (`python3 otomatis/discord.py status`):
   - status `tayang` → berhenti tanpa mengirim apa pun.
   - status `approved` → lanjut.
   - status lain (`menunggu-review`, `revisi`, …) → **jangan posting**. Kirim: "⏸️ Carousel hari ini belum di-approve, jadi belum tayang. Klik ✅ di pesan review; aku cek lagi jam 21.00." Berhenti.
3. `python3 otomatis/instagram.py posting` → memakai slide dari pesan hasil Discord terakhir + `caption.txt`, menulis `posting` di state dan `TAYANG …` di `STATUS.txt`.
4. Kirim: "📣 Sudah tayang di IG @seakun.id: <permalink>".
5. Commit + push.
- Sesi 21.00 di hari posting: ulangi langkah 2–5 (untuk carousel yang baru di-approve sore). Kalau masih belum approved, berhenti diam-diam.
- **Jangan** memakai `--paksa` kecuali user memintanya langsung. Posting tidak bisa dibatalkan dari sini; kalau salah tayang, minta tim menghapus manual di app Instagram.

## Akses Meta (sudah aktif sejak 21 Nov 2026)
App Meta "Seakun Autopost" (use case Instagram API, Unified login) di business portfolio Seakun; System-user token (tidak kedaluwarsa) dengan izin `instagram_basic` + `instagram_content_publish`, disimpan sebagai network secret untuk `graph.facebook.com`. IG user ID: lihat `config.json` → `instagram.ig_user_id`. Kuota API: 100 posting / 24 jam.
