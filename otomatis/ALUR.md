# Alur otomatis carousel pilar 2 via Discord

Panduan untuk **Naka di sesi cloud terjadwal**. Setiap sesi terjadwal mulai dari nol (repo baru di-clone, tanpa ingatan), jadi semua langkah dan state ada di sini dan di `otomatis/state.json`.

- **Jadwal (keputusan user 26 Nov 2026, menggantikan jadwal harian 21 Nov).** Carousel tayang **Sabtu, Senin, dan Kamis 17.00 WIB** (3× seminggu). Semua jam WIB (Asia/Jakarta, UTC+7).
  | Jam | Sesi | Kapan |
  |---|---|---|
  | 06.35 (target terkirim 07.00) | A. kirim radar topik | Senin & Jumat |
  | 10.02 | B. kumpulkan suara + plot (kalau belum) + produksi carousel hari ini | Senin, Kamis, Sabtu |
  | 12.07, 15.07 | C. cek feedback & revisi | Senin, Kamis, Sabtu |
  | 16.50 | C lalu D. posting ke IG (target 17.00) | Senin, Kamis, Sabtu |
- Radar Senin → 2 topik untuk **Senin + Kamis** (suara sampai Senin 10.00); radar Jumat → 1 topik untuk **Sabtu** (suara sampai Sabtu 10.00, diplot di sesi produksi Sabtu). Topik per hari ada di `state.json` → `harian.<tanggal>.terpilih` (diisi `discord.py plot`).
- **Bukan hari tayang (Selasa, Rabu, Jumat, Minggu) → sesi B, C, D langsung berhenti** tanpa mengirim apa pun (`discord.py status` → `hari_tayang: false`). Ini pengaman kalau tugas terjadwal masih berjalan setiap hari.
- **Tidak ada ✅ sampai 17.00 → tetap tayang** (keputusan user). Feedback tim tetap dikerjakan dulu, termasuk permintaan ganti topik hari itu.
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

## A. Kirim radar topik (Senin & Jumat, mulai ± 06.35, target terkirim ± 07.00)
1. `SIKLUS=$(TZ=Asia/Jakarta date +%F)`. Kalau `python3 otomatis/discord.py status` → `siklus_radar.siklus` sudah = `$SIKLUS` (radar hari ini sudah terkirim), **berhenti**.
2. Radar topik:
   - Kalau `konten/laporan/$SIKLUS_radar-topik.md` sudah ada, pakai itu.
   - Kalau belum: panggil **Sera** (radar saja: `trends.py` + `APIFY_LEWAT_PROXY=1 python3 collect.py --only ig_akun` + `analyze.py`, ± $0,2) → **Lira** tulis `konten/laporan/$SIKLUS_radar-topik.md` (10 topik + skor, format tabel sama dengan radar sebelumnya). Beri tahu Lira topik yang **sudah dipakai** (lihat `terpilih` di `otomatis/state.json` dan folder `konten/visual/`) supaya tidak diulang, dan kalender pemicu 2 minggu ke depan.
   - Hemat Apify: radar hanya Senin & Jumat (± $0,2 per radar).
   - Kalau Sera gagal (mis. kredit Apify < $1 atau host ditolak): Lira tetap menulis radar dari Google Trends + topik radar sebelumnya yang belum dipakai + cadangan, dan menulis keyakinan "rendah". Kalau semuanya gagal, kirim ke Discord: radar gagal dibuat + alasannya, lalu berhenti.
3. `python3 otomatis/discord.py kirim-topik konten/laporan/${SIKLUS}_radar-topik.md --siklus $SIKLUS`
4. Commit + push.

## B. Produksi (Senin, Kamis, Sabtu, 10.02)
`HARI=$(TZ=Asia/Jakarta date +%F)`
0. `python3 otomatis/discord.py status` → kalau `hari_tayang` false, **berhenti** tanpa mengirim apa pun.
1. **Plot topik dulu kalau belum.** Kalau siklus radar terbaru (`status` → `siklus_radar`) statusnya `menunggu-pilihan` (Senin: radar pagi ini; Sabtu: radar Jumat kemarin):
   - `python3 otomatis/discord.py baca-pilihan` → JSON (`suara`, `usulan`, `komentar_lain`, `plot_otomatis`).
   - `plot_otomatis` = usulan tim ("usul: …", terbaru dulu) → suara terbanyak (seri → bobot lebih tinggi) → bobot tertinggi, satu topik per hari tayang (radar Senin: Senin + Kamis; radar Jumat: Sabtu). Urutan hari tidak penting (keputusan user).
   - **Nomor yang dilihat tim = urutan emoji di pesan Discord (`urut`/`emoji` di JSON), bukan `no` radar.** Selalu sebut topik dengan emoji + judul di Discord. Baca `komentar_lain`: pilihan dalam kata-kata ("nomor 3 aja" = emoji 3️⃣) dihitung seperti suara. Usulan harus **lolos batasan** `konten/brand/brand.md` + aturan wajib `konten/pilar/fakta-unik/formula.md`; kalau tidak, ganti dengan topik berikutnya dan jelaskan dengan sopan di Discord.
   - Simpan + umumkan: `python3 otomatis/discord.py plot --kirim` (pakai `plot_otomatis`), atau `plot --kirim --pilihan '[{"tanggal":"…","no":3,"judul":"…","cara":"suara-tim"}, …]'` kalau Naka menyesuaikan. Pesan jadwal tersimpan sebagai `pesan_jadwal`.
2. **Cek permintaan tukar topik.** `python3 otomatis/discord.py baca-balasan <siklus_radar.pesan_jadwal>` (dari `status`). Permintaan "ganti <hari>: …" untuk hari ini atau hari lain dalam siklus → `tandai --hari <tgl> --terpilih '{"judul":"…","cara":"permintaan-tim","oleh":"…","no":null}'` (hanya kalau hari itu belum `produksi`/`tayang`; kalau hari ini sudah diproduksi, kerjakan di C). Lalu `tandai --balasan <id,…>`.
3. Ambil topik hari ini: `python3 otomatis/discord.py status` → `carousel.terpilih`.
   - Status sudah `produksi`/`menunggu-review`/`approved`/`tayang` → berhenti (sudah dikerjakan sesi lain).
   - Tidak ada entri hari ini (plot kosong, mis. radar gagal) → pilih sendiri topik bobot tertinggi yang belum dipakai dari radar terbaru, lalu `tandai --hari $HARI --terpilih '{…}'`.
   - Buat KODE `C-<SATU-KATA-KUNCI>` (huruf besar, mis. `C-HARBOLNAS`) dan folder `konten/visual/$HARI_<KODE>/` (tanggal posting = **hari ini**).
   `python3 otomatis/discord.py tandai --status produksi --terpilih '{"kode":"C-…","folder":"konten/visual/…"}'`
   `python3 otomatis/discord.py kirim "🛠️ Carousel hari ini: **…**. Lagi dikerjakan, hasilnya aku kirim ke sini ± 11.30–12.00; tayang 17.00 WIB."`
4. Produksi (sama dengan alur manual di `CLAUDE.md`, dengan penyesuaian mode otomatis):
   - **Riset fakta oleh Naka** (WebSearch/WebFetch): kumpulkan angka & tanggal bersumber untuk "Data yang perlu dicari" di baris radar. Simpan catatan sumber di draft. Jangan mengarang angka; yang tidak terverifikasi ditandai `[CEK FAKTA]` lalu dibuang atau diganti sebelum render final.
   - **Diksa** → `konten/draft/<tanggal posting>_<slug>.md` (wajib baca `brand.md` + `konten/pilar/fakta-unik/formula.md`; contoh lulus: `konten/draft/2026-11-19_gaji-naik-pas-pasan.md`).
   - **Rupa, mode otomatis**: format berita/data seperti C-GAJI (`konten/visual/2026-11-19_C-GAJI/spec.json`), **tidak menunggu ilustrasi ChatGPT dari user**. Wajib baca `visual.md`, `brand.md`, `konten/pilar/fakta-unik/formula.md`. Hasil: `slide-*.png` + `caption.txt` (**tanpa sumber & tanpa hashtag**) + `spec.json` + `foto/SUMBER.md`.
     - **Gaya cover digilir (user, 26 Nov 2026)**: sebelum membuat foto cover, `python3 konten/brand/visual/gaya_cover.py --kecuali <folder>` → gaya (`lingkar`/`editorial`/`poster`) + arahan komposisi foto. Pakai arahan itu di prompt ElevenLabs, dan teruskan gaya ke Rupa (`"kartu": "<gaya>"` di slide 1). Jangan memakai gaya yang sama dengan carousel sebelumnya.
     - **Cover (slide 1) → ElevenLabs, dibuat Naka** (aturan tetap di `konten/pilar/fakta-unik/aturan.md`), anggaran **± 1.000 kredit per cover**:
       1. `creative_generate_image` model `gpt-image-2.5-sunburst`, `generations_count` 1. Prompt: foto sinematik nyata suasana Indonesia, posisi subjek & area kosong **sesuai arahan `gaya_cover.py`** (lingkar: atas kosong; editorial: bawah kosong; poster: kiri kosong), layar TV/HP hanya cahaya buram tanpa orang, **tanpa teks, tanpa logo, tanpa wajah orang sungguhan**. Poster/cuplikan berhak cipta hanya acuan gaya di prompt.
       2. Panggilan pertama keluar 16:9 1K (default, ± 190 kredit). Jangan pakai hasil itu untuk cover: langsung `creative_update_node` (node dari hasil tadi) `model_parameters {"aspect_ratio":"4:5","resolution":"2K","quality":"high"}` lalu `creative_run_flow_nodes` (± 471 kredit). Kalau node bisa diatur sebelum jalan (buat flow + node dulu), lakukan itu supaya hanya bayar 1× 2K.
       3. Tunggu `creative_get_flow_run_status`, unduh `content_url` ke `<folder>/foto/cover-el.png` (host `elevenlabsusercontent.com`), lihat hasilnya.
       4. Total maks ± 1.000 kredit; jangan memanggil ulang untuk "retry". Catat model, flow_id, kredit (`price.credits` tiap generation) di `foto/SUMBER.md` dan di pesan Discord saat kirim hasil.
       5. Kalau tool ElevenLabs tidak tersedia di sesi ini atau unduhan diblokir proxy, pakai `gambar.py ai`/stok Magnific untuk cover, dan sebutkan alasannya + host yang diblokir di pesan Discord.
     - **Slide CTA**: kotak harga otomatis dari `brand.json` `cta_harga` (desain C-GAJI). Jangan menulis `layanan` di spec. **Gaya wajib seperti C-SINETRON** (user, 26 Nov 2026): latar foto blur (default foto cover), logo provider blur, tombol `tap`, tanpa footer; semuanya default `render.py`, jadi jangan menulis `tombol`/`footer`/`bar_kanan`/`logo_blur` di slide CTA. Lihat `konten/pilar/fakta-unik/aturan.md` no. 1b.
     - **Slide 2 dst. yang menyebut nama spesifik → Sidik** (Google Images via Apify, ± $0,1 per carousel; panggil sebelum Rupa, teruskan path draft + folder + daftar slide). Rupa memasang `foto/<slug>.jpg` + `kredit` dari laporan Sidik. Gambar dari tim di Discord/Drive tetap didahulukan kalau ada.
     - **Slide 2 dst. bertema umum → Magnific** lewat `konten/brand/visual/gambar.py` (stok, `wiki` untuk foto faktual). Izin kredit Magnific: maks 1 unduhan per slide + maks 1 generate `ai` (hanya kalau stok tidak ada).
   - **Tilik titik cek 3** pada PNG final (+ cek 2 pada foto yang diunduh). Temuan → Rupa perbaiki → Tilik lagi, maks 3 putaran.
   - Versi Canva: kalau `konten/brand/visual/canva.py` ada, `python3 konten/brand/visual/canva.py <folder>/spec.json`.
   - `echo "MENUNGGU REVIEW $(TZ=Asia/Jakarta date +%F) (Discord)" > <folder>/STATUS.txt`
5. `python3 otomatis/discord.py kirim-hasil <folder>` (slide, caption, PDF Canva, pesan review dengan ✅; pesannya menyebut tayang 17.00 walau belum ✅).
   Kalau masih ada temuan Tilik yang belum beres setelah 3 putaran, tetap kirim dengan `--catatan "⚠️ Catatan QA: …"`.
6. Commit + push. Kalau produksi gagal di tengah jalan: `tandai --status gagal`, kirim ke Discord apa yang gagal dan apa yang dibutuhkan, commit yang sudah jadi.

## C. Cek feedback (Senin, Kamis, Sabtu 12.07, 15.07, dan awal sesi 16.50)
`HARI=$(TZ=Asia/Jakarta date +%F)`
1. `python3 otomatis/discord.py status`. Kalau `hari_tayang` false, carousel hari ini belum punya `hasil`, atau status `tayang`, **berhenti tanpa mengirim apa pun** (sesi B belum selesai / sudah tayang).
2. `python3 otomatis/discord.py baca-feedback` → JSON. Cek juga `baca-balasan <pesan_jadwal>` untuk permintaan tukar topik hari ini.
3. Ada `feedback_baru` → **revisi dulu** (feedback menang atas ✅ yang lebih lama):
   - `tandai --status revisi`. Kirim: "📝 Feedback diterima dari …, lagi aku kerjakan."
   - **Ganti topik hari ini** ("ganti topik: …") → `tandai --terpilih '{"judul":"…","cara":"permintaan-tim","oleh":"…"}'`, produksi ulang seperti B langkah 3–4 dengan KODE/folder baru. Kalau sudah lewat 15.30 dan tidak akan selesai sebelum 17.00, kirim ke Discord bahwa topik baru tayang ± 1 jam lebih lambat, lalu tetap kerjakan.
   - Selain itu: teruskan poin feedback **apa adanya** ke Rupa (visual) atau Diksa (isi teks/angka; lalu Rupa render ulang) → Tilik titik cek 3 → canva.py lagi.
   - Lampiran gambar dari tim (URL `cdn.discordapp.com`) boleh diunduh ke `<folder>/foto/` kalau diminta dipakai.
   - Kalau feedback tidak jelas atau melanggar batasan brand, tanyakan balik di Discord (`kirim "…" --balas <id pesan>`) dan jangan menebak; carousel versi terakhir tetap tayang 17.00.
   - `kirim-hasil <folder> --revisi <N+1> --catatan "Yang diubah: …"`, lalu `tandai --feedback <id1,id2,…>` (status kembali `menunggu-review`).
4. Tidak ada feedback baru dan ada `approve` (✅) atau `approve_lewat_teks` → **APPROVED**:
   - `echo "APPROVED $(TZ=Asia/Jakarta date +%F) (Discord: <nama>)" > <folder>/STATUS.txt`, `tandai --status approved`.
   - Kirim: "✅ Approved oleh …. Tayang di IG @seakun.id hari ini 17.00 WIB."
5. Tidak ada apa-apa → berhenti tanpa mengirim apa pun (di sesi 16.50 lanjut ke D).
6. Commit + push kalau ada perubahan.

## D. Posting ke Instagram (Senin, Kamis, Sabtu, sesi 16.50 → tayang ± 17.00)
1. Jalankan C dulu (feedback terakhir dikerjakan sebelum tayang). Lalu `python3 otomatis/instagram.py cek` (token + kuota). Gagal (401/190/tunnel 403) → kirim ke Discord "⚠️ Posting IG gagal: token/akses Meta bermasalah (…)", berhenti.
2. `python3 otomatis/discord.py status`:
   - `hari_tayang` false atau status `tayang` → berhenti tanpa mengirim apa pun.
   - status `approved` atau `menunggu-review` → lanjut. **Tanpa ✅ tetap tayang** (keputusan user 21 Nov 2026).
   - status `produksi`/`revisi` (masih dikerjakan) → selesaikan dulu di sesi ini (B/C), kirim hasilnya, lalu posting. Kalau gagal total (`gagal`/tidak ada hasil), kirim "⚠️ Carousel hari ini batal tayang: …" dan berhenti.
3. Kalau sesi selesai sebelum 17.00, tunggu sampai 17.00 WIB (`python3 -c "import time; time.sleep(N)"`, maks ± 10 menit), lalu `python3 otomatis/instagram.py posting` → slide dari pesan hasil Discord terakhir + `caption.txt`, menulis `posting` di state dan `TAYANG …` di `STATUS.txt`.
4. Kirim: "📣 Sudah tayang di IG @seakun.id: <permalink>" (+ "(tanpa ✅)" kalau `tanpa_approve`).
5. Commit + push.
- **Jangan** memakai `--paksa` kecuali user memintanya langsung. Posting tidak bisa dibatalkan dari sini; kalau salah tayang, minta tim menghapus manual di app Instagram.

## Akses Meta (sudah aktif sejak 21 Nov 2026)
App Meta "Seakun Autopost" (use case Instagram API, Unified login) di business portfolio Seakun; System-user token (tidak kedaluwarsa) dengan izin `instagram_basic` + `instagram_content_publish`, disimpan sebagai network secret untuk `graph.facebook.com`. IG user ID: lihat `config.json` → `instagram.ig_user_id`. Kuota API: 100 posting / 24 jam.
