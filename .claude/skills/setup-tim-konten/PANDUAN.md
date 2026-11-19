# Pindahkan Tim Konten (Naka & tim) ke Brand Lain

Isi kit ini: skill **`setup-tim-konten`**, yaitu template seluruh tim (Naka, Sera, Lira, Kala, Diksa, Rupa, Tilik), skrip riset, mesin visual (render.py, check.py, ilustrasi.py), dan panduan kerapian visual. Semua bagian khusus ANAKU sudah diganti placeholder.

**Tidak ikut** (sengaja): token Apify, webhook/token Discord, token Instagram, data riset, draft, dan visual ANAKU, serta logo/font ANAKU.

## Syarat
Kit ini butuh **Claude Code** (tab Code di aplikasi desktop, atau `claude` di terminal) di **Mac** dengan Google Chrome dan Python 3. Kit ini tidak bisa dipakai di chat claude.ai biasa, karena tim perlu membaca/menulis file dan merender PNG di komputer.

## Cara pasang
1. **Login ke akun Claude yang lain** di Claude Code.
2. **Taruh skill-nya di folder skill pribadi:** salin folder `setup-tim-konten` ke `~/.claude/skills/`, sehingga jadi `~/.claude/skills/setup-tim-konten/SKILL.md`.
   - Kalau di komputer lain: kirim `tim-konten-kit.zip`, ekstrak, lalu salin foldernya ke tempat yang sama.
   - Catatan: di Mac yang sama, folder `~/.claude/skills/` dipakai bersama oleh semua akun Claude yang login di user Mac itu.
3. **Buat folder kosong untuk brand baru**, misalnya `~/Konten KopiSenja`, lalu buka folder itu di Claude Code.
4. Ketik: **"setup tim konten untuk brand <nama>"** (atau `/setup-tim-konten`). Claude akan:
   - mewawancarai kamu soal brand (bisa dibantu link situs/brand kit)
   - memasang semua file dan mengisi profil brand, warna, font, tagline, dan footer
   - meminta logo, font, dan contoh post brand
   - menguji render 3 slide contoh dan menunjukkannya untuk kamu setujui
5. Isi token Apify **sendiri** di `riset/.env` (akun Apify gratis, boleh akun terpisah dari ANAKU).
6. **Tutup lalu buka lagi** sesi di folder itu. Setelah itu "Naka, riset tren" langsung jalan.

## Yang perlu diperhatikan
- **Satu brand = satu folder.** Jangan campur dua brand di satu folder.
- **Font:** pastikan lisensi font brand baru boleh dipakai.
- **Kredit Apify:** kalau dua brand memakai akun Apify yang sama, jatah gratis $5/bulan dibagi dua (sekitar 3 riset penuh per brand per bulan).
- **Modul lanjutan belum ikut:** auto-posting IG, bot Discord, pemantau latar belakang, dan generate ilustrasi otomatis lewat bot. Bisa dipasang terpisah nanti, dengan token dan nama layanan khusus untuk brand itu.
- Kalau ada aturan baru dari revisi di brand ANAKU yang ingin dibawa ke brand lain, minta Naka memperbarui kit ini (`export/tim-konten-kit/`) lalu pasang ulang skill-nya.
